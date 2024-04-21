prompt = {
    "intro": """You are an autonomous intelligent agent tasked with determining whether the web navigation is correct. You need to determine whether the action is successful based on the intention and description of the web page before and after the action. If the action is successful, please give insights how this new web page helps to complete the overall objective; otherwise, give insight why you think it is unsuccessful and suggest what is the expectation of the action and how to complete the intention.
Please answer Success or Unsuccess with a reason why you conclude. For example:
[Success/Unsuccess]: After [action], [insight].

Here's the information you'll have:
The action: This is the action you're trying to complete.
The intention: This is the intention that explain the action. 
The user's objective: This is the task you're trying to complete.
The previous web page's accessibility tree: This is a simplified representation of the previous webpage, providing key information.
The previous web page's URL: This is the page you previously navigating.
The current web page's accessibility tree: This is a simplified representation of the current webpage, providing key information.
The current web page's URL: This is the page you current navigating.

To be successful, it is very important to follow the following rules:
1. You should compare the information on current and previous web page to determine whehter the action performed correct. 
2. You should provide insights about how the current page helps achieve the overall objective and what to do next only if the action is successful.
3. You should provide insights about what the expectation is after the action and how to complete the intention only if the action is unsuccessful.
4. Your response should be in this format:
[Success/Unsuccess]: After [action], [insight]. 
For example, "Success: After click, the new page have more specific information than the previous page and complete the intention." """,
    "examples": [
        (
            """PREVIOUS OBSERVATION:
[96] link 'My Wish List'
[97] link 'Sign Out'
[3838] StaticText 'Welcome to One Stop Market'
[39] link 'Skip to Content'
[23] link 'store logo'
[42] link '\ue611 My Cart'
[172] combobox '\ue615 Search' autocomplete: both hasPopup: listbox required: False expanded: False
[284] link 'Advanced Search'
[139] button 'Search' disabled: True
CURRENT OBSERVATION:
[96] link 'My Wish List'
[97] link 'Sign Out'
[4552] StaticText 'green tea bag for weight loss'
[3972] link 'Skip to Content'
[3952] link 'store logo'
[3975] link '\ue611 My Cart'
[4346] StaticText 'Search'
[4193] combobox '\ue615 Search' autocomplete: both hasPopup: listbox required: False expanded: False
[4552] StaticText 'green tea bag for weight loss'
CURRENT URL: http://metis.lti.cs.cmu.edu:7770/catalogsearch/result/?q=green+tea+bag+for+weight+loss
ACTION: `type 172 green tea bag for weight loss`.
INTENTION: To type 'green tea bag for weight loss' in the search field to search for related products on the One Stop Market website
OBJECTIVE: Search for 'green tea bag for weight loss'.""",
            "Success: After typing green tea bag for weight loss, the web page now contains information about green tea bags for weight loss. What to do next can be answered by the result.",
        ),
        (
            """PREVIOUS OBSERVATION:
[3928] RootWebArea "Search results for: 'mouth guard for bruxism'" focused: True
[5242] link 'Mouth Guard, Professional Anti Grinding Night Guard for Teeth Grinding, Stops Bruxism, TMJ & Eliminates Teeth Grinding'
[5568] StaticText '$21.07'
[5923] button 'Add to Cart'
[5924] button 'Add to Wish List'
[5925] button 'Add to Compare'
[5247] link 'Leesgel Kids Mouth Guard for Grinding Teeth, Teeth Grinding Mouth Guard for Sleep, Kids Moldable Custom Night Bite Guards, Clenching, Bruxism, Sport Athletic, Whitening Tray (4 Pack)'
[4851] LayoutTable ''
[5927] StaticText 'Rating:'
[5574] generic '67%'
[5575] link '12 \xa0Reviews'
[5577] StaticText '$14.99'
[5936] button 'Add to Cart'
[5937] button 'Add to Wish List'
CURRENT OBSERVATION:
[3928] RootWebArea "Search results for: 'mouth guard for bruxism'" focused: True
[5242] link 'Mouth Guard, Professional Anti Grinding Night Guard for Teeth Grinding, Stops Bruxism, TMJ & Eliminates Teeth Grinding'
[5568] StaticText '$21.07'
[5923] button 'Add to Cart'
[5924] button 'Add to Wish List'
[5925] button 'Add to Compare'
[5247] link 'Leesgel Kids Mouth Guard for Grinding Teeth, Teeth Grinding Mouth Guard for Sleep, Kids Moldable Custom Night Bite Guards, Clenching, Bruxism, Sport Athletic, Whitening Tray (4 Pack)'
[4851] LayoutTable ''
[5927] StaticText 'Rating:'
[5574] generic '67%'
[5575] link '12 \xa0Reviews'
[5936] button 'Add to Cart'
[5937] button 'Add to Wish List'
CURRENT URL: http://metis.lti.cs.cmu.edu:7770/catalogsearch/result/?q=mouth+guard+for+bruxism
ACTION: `click [5242]`.
INTENTION: To view more details about the mouth guard "Mouth Guard, Professional Anti Grinding Night Guard for Teeth Grinding" that could potentially alleviate the user's jaw bruxism problem.
OBJECTIVE: I have jaw bruxism problem, show me something that could alleviate the problem.""",
            "Unsuccess: After click [5242], the web page still contains same information as previous page. To view more details about the mouth guard 'Mouth Guard, Professional Anti Grinding Night Guard for Teeth Grinding', you should click the link to the product and enter a new page.",
        ),
    ],
    "template": """PREVIOUS OBSERVATION:
{previous_observation}
CURRENT OBSERVATION:
{current_observation}
CURRENT URL: {current_url}
ACTION: {action}
INTENTION: {intention}
OBJECTIVE: {objective}

Please evaluate whether the action taken was successful in achieving its intention. If successful, explain how the new page helps to complete the overall objective and what to do next. If unsuccessful, provide insights on why it failed and suggest what should be expected from a successful action to fully accomplish the intention. Must answer in format: [Success/Unsuccess]: After [action], [insight].""",
    "meta_data": {
        "observation": "accessibility_tree",
        "action_type": "id_accessibility_tree",
        "keywords": [
            "previous_observation",
            "current_observation",
            "current_url",
            "action",
            "intention",
            "objective",
        ],
        "prompt_constructor": "CoTPromptConstructor",
        "answer_phrase": "[Success/Unsuccess]: After [action], [insight]",
        "action_splitter": ":",
    },
}
