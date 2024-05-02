import argparse
import json
from typing import Any

import tiktoken
from beartype import beartype

from agent.prompts import *
from browser_env import Trajectory
from browser_env.actions import (
    Action,
    ActionParsingError,
    create_id_based_action,
    create_none_action,
    create_playwright_action,
)
from browser_env.utils import Observation, StateInfo
from llms import (
    call_llm,
    generate_from_huggingface_completion,
    generate_from_openai_chat_completion,
    generate_from_openai_completion,
    lm_config,
)
from llms.tokenizers import Tokenizer


class Agent:
    """Base class for the agent"""

    def __init__(self, *args: Any) -> None:
        pass

    def next_action(
        self, trajectory: Trajectory, intent: str, meta_data: Any
    ) -> Action:
        """Predict the next action given the observation"""
        raise NotImplementedError

    def reset(
        self,
        test_config_file: str,
    ) -> None:
        raise NotImplementedError


class TeacherForcingAgent(Agent):
    """Agent that follows a pre-defined action sequence"""

    def __init__(self) -> None:
        super().__init__()

    def set_action_set_tag(self, tag: str) -> None:
        self.action_set_tag = tag

    def set_actions(self, action_seq: str | list[str]) -> None:
        if isinstance(action_seq, str):
            action_strs = action_seq.strip().split("\n")
        else:
            action_strs = action_seq
        action_strs = [a.strip() for a in action_strs]

        actions = []
        for a_str in action_strs:
            try:
                if self.action_set_tag == "playwright":
                    cur_action = create_playwright_action(a_str)
                elif self.action_set_tag == "id_accessibility_tree":
                    cur_action = create_id_based_action(a_str)
                else:
                    raise ValueError(f"Unknown action type {self.action_set_tag}")
            except ActionParsingError as e:
                cur_action = create_none_action()

            cur_action["raw_prediction"] = a_str
            actions.append(cur_action)

        self.actions: list[Action] = actions

    def next_action(
        self, trajectory: Trajectory, intent: str, meta_data: Any
    ) -> Action:
        """Predict the next action given the observation"""
        return self.actions.pop(0)

    def reset(
        self,
        test_config_file: str,
    ) -> None:
        with open(test_config_file) as f:
            ref_actions = json.load(f)["reference_action_sequence"]
            tag = ref_actions["action_set_tag"]
            action_seq = ref_actions["action_sequence"]
            self.set_action_set_tag(tag)
            self.set_actions(action_seq)


class PromptAgent(Agent):
    """prompt-based agent that emits action given the history"""

    @beartype
    def __init__(
        self,
        action_set_tag: str,
        lm_config: lm_config.LMConfig,
        prompt_constructor: PromptConstructor,
    ) -> None:
        super().__init__()
        self.lm_config = lm_config
        self.prompt_constructor = prompt_constructor
        self.action_set_tag = action_set_tag

    def set_action_set_tag(self, tag: str) -> None:
        self.action_set_tag = tag

    @beartype
    def next_action(
        self, trajectory: Trajectory, intent: str, meta_data: dict[str, Any]
    ) -> Action:
        prompt = self.prompt_constructor.construct(trajectory, intent, meta_data)
        lm_config = self.lm_config
        n = 0
        while True:
            response = call_llm(lm_config, prompt)
            force_prefix = self.prompt_constructor.instruction["meta_data"].get(
                "force_prefix", ""
            )
            response = f"{force_prefix}{response}"
            n += 1
            try:
                parsed_response = self.prompt_constructor.extract_action(response)
                if self.action_set_tag == "id_accessibility_tree":
                    action = create_id_based_action(parsed_response)
                elif self.action_set_tag == "playwright":
                    action = create_playwright_action(parsed_response)
                else:
                    raise ValueError(f"Unknown action type {self.action_set_tag}")
                action["raw_prediction"] = response
                break
            except ActionParsingError as e:
                if n >= lm_config.gen_config["max_retry"]:
                    action = create_none_action()
                    action["raw_prediction"] = response
                    break

        return action

    def reset(self, test_config_file: str) -> None:
        pass


class ReflectAgent(Agent):
    """prompt-based agent that emits action given the history and reflect after each action"""

    @beartype
    def __init__(
        self,
        action_set_tag: str,
        lm_config: lm_config.LMConfig,
        intention_prompt_constructor: IntentionPromptConstructor,
        insight_prompt_constructor: InsightPromptConstructor,
        intention_model: str,
        insight_model: str,
    ) -> None:
        super().__init__()
        self.lm_config = lm_config
        self.intention_prompt_constructor = intention_prompt_constructor
        self.insight_prompt_constructor = insight_prompt_constructor
        self.intention_model = intention_model
        self.insight_model = insight_model
        self.action_set_tag = action_set_tag
        self.intention = ""
        self.insight = ""
        self.first = True

    def set_action_set_tag(self, tag: str) -> None:
        self.action_set_tag = tag

    @beartype
    def next_action(
        self, trajectory: Trajectory, intent: str, meta_data: dict[str, Any]
    ) -> Action:
        # generate insight from previous action
        if not self.first:
            prompt = self.insight_prompt_constructor.construct(
                trajectory, intent, self.intention, meta_data
            )
            lm_config = self.lm_config
            lm_config.model = self.insight_model
            n = 0
            while True:
                response = call_llm(lm_config, prompt)
                force_prefix = self.insight_prompt_constructor.instruction[
                    "meta_data"
                ].get("force_prefix", "")
                response = f"{force_prefix}{response}"
                n += 1
                try:
                    self.insight = self.insight_prompt_constructor.extract_action(
                        response
                    )
                    break
                except ActionParsingError as e:
                    if n >= lm_config.gen_config["max_retry"]:
                        self.insight = ""
                        break
        else:
            self.first = False
            self.insight = ""

        prompt = self.intention_prompt_constructor.construct(
            trajectory, intent, self.insight, meta_data
        )
        lm_config = self.lm_config
        lm_config.model = self.intention_model
        n = 0
        while True:
            response = call_llm(lm_config, prompt)
            force_prefix = self.intention_prompt_constructor.instruction[
                "meta_data"
            ].get("force_prefix", "")
            response = f"{force_prefix}{response}"
            n += 1
            try:
                parsed_response, self.intention = (
                    self.intention_prompt_constructor.extract_action(response)
                )
                if self.action_set_tag == "id_accessibility_tree":
                    action = create_id_based_action(parsed_response)
                elif self.action_set_tag == "playwright":
                    action = create_playwright_action(parsed_response)
                else:
                    raise ValueError(f"Unknown action type {self.action_set_tag}")
                action["raw_prediction"] = response
                break
            except ActionParsingError as e:
                if n >= lm_config.gen_config["max_retry"]:
                    action = create_none_action()
                    action["raw_prediction"] = response
                    self.intention = ""
                    break

        return action

    def reset(self, test_config_file: str) -> None:
        self.first = True
        self.insight = ""


def construct_agent(args: argparse.Namespace) -> Agent:
    llm_config = lm_config.construct_llm_config(args)

    agent: Agent
    if args.agent_type == "teacher_forcing":
        agent = TeacherForcingAgent()
    elif args.agent_type == "prompt":
        with open(args.instruction_path) as f:
            constructor_type = json.load(f)["meta_data"]["prompt_constructor"]
        tokenizer = Tokenizer(args.provider, args.model)
        prompt_constructor = eval(constructor_type)(
            args.instruction_path, lm_config=llm_config, tokenizer=tokenizer
        )
        agent = PromptAgent(
            action_set_tag=args.action_set_tag,
            lm_config=llm_config,
            prompt_constructor=prompt_constructor,
        )
    elif args.agent_type == "reflect":
        tokenizer = Tokenizer(args.provider, args.model)
        intention_prompt_constructor = IntentionPromptConstructor(
            args.intention_instruction_path, lm_config=llm_config, tokenizer=tokenizer
        )
        insight_prompt_constructor = InsightPromptConstructor(
            args.insight_instruction_path, lm_config=llm_config, tokenizer=tokenizer
        )
        agent = ReflectAgent(
            action_set_tag=args.action_set_tag,
            lm_config=llm_config,
            intention_prompt_constructor=intention_prompt_constructor,
            insight_prompt_constructor=insight_prompt_constructor,
            intention_model=args.intention_model,
            insight_model=args.insight_model,
        )
    else:
        raise NotImplementedError(f"agent type {args.agent_type} not implemented")
    return agent
