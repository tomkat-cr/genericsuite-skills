# Generic CRUD Editor Configuration Documentation

This documentation provides configuration specifications for the Generic CRUD Editor JSON files.

## Configuration directory

The configuration directory is where the Generic CRUD Editor JSON files are stored. The suggested directory structure is:

```text
.
├── CHANGELOG.md
├── README.md
├── backend
│   ├── app_main_menu.json
│   ├── endpoints.json
│   ├── general_config.json
│   ├── users.json
│   └── users_config.json
└── frontend
    ├── app_constants.json
    ├── general_config.json
    ├── general_constants.json
    ├── users.json
    ├── users_config.json
    └── users_profile.json
```

## Frontend Configuration

The frontend configuration defines the overall behavior of the CRUD editor and is used by both the frontend and backend.

The frontend configuration is located in the `frontend` directory.

In the frontend configuration directory, there are several JSON files, most of them are CRUD editor configurations, and there are three special files:

* `app_constants.json`
* `general_constants.json`
* `general_config.json`

Check the [Frontend directory](./index.md#frontend-directory) section in the [GenericSuite App Creation and Configuration guide](./index.md) for more details.

### Validation

The validation configuration defines the validation rules for the CRUD editor.

The TypeScript interfaces to validate the frontend JSON configurations are defined in the [CrudEditorConfigInterface.ts](https://github.com/tomkat-cr/genericsuite-basecamp/blob/main/docs/code/configuration-guide/CrudEditorConfigInterface.ts) file (`FrontendCrudEditorConfig`, `ParentKeyName`, `FieldElement`, `FieldType`).

The Python classes to validate the frontend JSON configurations are defined in the [crud_editor_config_classes.py](https://github.com/tomkat-cr/genericsuite-basecamp/blob/main/docs/code/configuration-guide/crud_editor_config_classes.py) file (`FrontendCrudEditorConfig`, `ParentKeyName`, `FieldElement`, `FieldType`).

### General Configuration

The JSON files for each table or CRUD editor in the example are `users.json`, `users_config.json`, and `users_profile.json`.

For those files, the general configuration section defines the overall behavior of the CRUD editor.

The following attributes are used in the general configuration section:

* **baseUrl**: The ReactJS router URL for the CRUD editor.
	+ Example: `ai_chatbot_conversations`

* **title**: The title of the CRUD editor, used in the listing page.
	+ Example: "AI Assistant Conversations"

* **name**: The name of the CRUD editor component, used as a title in the form submission page.
	+ Example: "AI Assistant Conversation"

* **component**: The ReactJS component name used by the CRUD editor. This component is the glue with the .json file and the registry of dependencies (or related components).
	+ Example: `AiChatBotConversations`

* **dbApiUrl**: The API endpoint URL that the CRUD editor interacts with.
	+ Example: `ai_chatbot_conversations`

* **primaryKeyName**: Primary Key parameter name for API calls
    + Example: `id`

* **defaultOrder**: The default order specifies the sorting criteria for data retrieved from the database in the listing page.
	+ Example: `defaultOrder": "update_date|desc` sorts data by `update_date` in descending order.

* **mandatoryFilters**: Mandatory filters are used to restrict access to certain fields or data. If it's specified, `mandatoryFiltersDbListPreRead` will be added to `dbListPreRead` and `mandatoryFiltersDbPreRead` will be added to `dbPreRead` specific functions.
	+ Example: to specify the ID of the current user who should be authorized to access the filtered data.
```json
"mandatoryFilters": {
    "user_id": "{CurrentUserId}"
},
```

* **userIdFilter**: Whether the current user ID filter should be added to the listing page. It's an alternative to the previous example given to the `mandatoryFilters` attribute.
    + Example: `true` or `false`

* **fieldElements**: List of field elements to be used in the child listing editor. More details in the [Field Elements](#field-elements) section.

### 1 to N Relationships

* **childComponents**: List of child components related to the main table.
    + Example: to have child listings with the `Users History` and `Users Configuration` components related to the `Users` main table:
```json
"childComponents": [
    "UsersUserHistory",
    "UsersConfig"
],
```

* **type**: editor type. Use `child_listing` for the child editors (1-to-many relationship), of `master_listing` for the main editor. Defaults to `master_listing`.
    + Example: `child_listing` or `master_listing`

* **subType**: tells the backend how to store the 1-to-many relationship. Use `array` for relationship items stored in the same parent table as an array element. Use `table` for relationship items stored in a different table.
    + Example: `array` or `table`

* **array_name**: attribute name for the `array` type child listing. For example, if the parent table is "table_x_header" and the child table is "table_x_lines", the `array_name` could be "table_x_lines".
    + Example: `table_x_lines`

* **parentUrl**: the parent table URL to be used on certain specific functions (because the parent table name is defined in the backend JSON file `table_name` attribute and frontend does not have access to it).
    + Example: `users` for the `/v1/users` endpoint.

* **endpointKeyNames**: Key Names array used when making API calls to the backend to get the child listing items. This is used to stabllish the relationship between the parent and child tables (1-to-many relationship). Each element of the array must have the following attributes:
    + `parameterName`: the name of the parameter to be used in the backend API call (endpoint) to identify the parent table Primary/Sort Key.
    + `parentElementName`: the name of the parent table's attribute which value will be used to identify the parent table Primary/Sort Key.<br><br>
    + Example:
```json
"type": "child_listing",
"subType": "array",
"array_name": "users_config",
"parentUrl": "users",
"endpointKeyNames": [
    {
        "parameterName": "user_id",
        "parentElementName": "id"
    }
],
```

* **allow_duplicates**: Allow duplicates in the child listing items creation. Defaults to `false`.
    + Example: `true` or `false`

### Field Elements

Field elements define the individual fields used in the CRUD editor.

* **name**: The name of the field element.

* **label**: The label displayed for the field.

* **type**: The data type of the field or `field type` for the field element. Check [Field data types](#field-data-types) for more details.

* **required**: Whether the field is required for submission.
	+ Example: `true`, `false`

* **listing**: Whether the field should be displayed in the listing page.
	+ Example: `true`, `false`

* **readonly**: Whether the field should be read-only.
	+ Example: `true`, `false`

* **primaryKey**: Whether the field is the primary key of the table.
	+ Example: `true`, `false`

* **default_value**: The default value to use for the field when the form data page is loaded.
	+ Example: `0` or `current_timestamp`. `current_timestamp` will be replaced by the current date/time.

* **hidden**: Whether the field should be hidden from display.
	+ Example: `true`, `false`

* **formula**: to get the field value from a ReactJS component. Check the [Formulas](#formulas) section for more details.

#### Field data types

* **text**: generates a text input field (single line).

* **textarea**: generates a textarea input field (multi line).

* **number**: generates a number input field (float).

* **integer**: generates a integer input field (no decimals).

* **date**: generates a date input field (date only).

* **datetime-local**: generates a datetime-local input field (date and time).

* **array**: generates an multidimensional array field, like the `dict` type in Python.
    + Examples: 
```json
"array": [
    {
        "key1": "value1",
        "key2": "value2"
    }
]
```
```json
"array": {
    "key1": {
        "key2": "value2"
    }
}
```

* **email**: generates an email input field (and validates it during the input).

* **label**: generates a label with no input field.

* **h1, h2, h3, h4, h5, h6**: generates a heading with the specified level.

* **hr**: generates a horizontal rule.

* **_id**: generates a hidden input field with the current object's primary key value.

* **select**: generates a select input field from a list of options.

* **select_table**: generates a select input field from a list of items in a related table.

* **select_component**: generates a select input field with a ReactJS component that populates the options from the database.

* **suggestion_dropdown**: generates a input field with a suggestion dropdown from the database or a API call. Check the [Suggestion Dropdowns](#suggestion-dropdowns) section for more details.

* **component**: shows a value generated from a ReactJS component.

#### Special buttons definitions

There are special buttons that can be used in the field elements. These buttoms will appear in the form data page only at the right side of the field.

The buttons are enabled by the `chatbot_popup` and `google_popup` attributes of the field element, and the `chatbot_prompt` and `google_prompt` attributes are used to define the text that will be used when calling the corresponding button ReacTJS component.

The special buttons definitions are optional.

* **chatbot_popup**: generates a button that uses the `ChatBotButton` ReactJS component which opens a popup to interact with the AI Assistant. Defaults to `false`.
    + Example: `chatbot_popup: true`.

* **chatbot_prompt**: defines the text that will be used when calling the `ChatBotButton` ReactJS component.
    + Example: `chatbot_prompt: "Give me all the information for the %s topic"`. __NOTE__: `%s` will be replaced by the field value.

* **google_popup**: generates a button that will call the `SearchEngineButton` ReactJS component. Defaults to `false`.
    + Example: `google_popup: true`

* **google_prompt**: defines the text that will be used when calling the `SearchEngineButton` ReactJS component.
    + Example: `google_prompt: "%s calories in KCAL, serving size amount and serving size unit"`. __NOTE__: `%s` will be replaced by the field value.

### Suggestion Dropdowns

Suggestion dropdowns are used to fill the input field value with suggestions shown in a dropdown list populated by a database or API call while the user is typing.

The suggestions are populated from a API URL defined in the `filter_api_url` attribute, and the `filter_api_request_method` attribute defines the HTTP method to be used to call the API.

The `suggestion_id_fieldname` attribute defines the field name in the API response that will be used to identify the selected item Key in the dropdown.

The `suggestion_desc_fieldname` attribute defines the field name in the API response that will be used to display the selected item Name in the dropdown.

The `filter_search_param_name` attribute defines the parameter name to be used in the API call to identify the search term.

The `filter_search_other_param` attribute is a dictionary that defines the other parameters to be used in the API call to identify the search term.

The `autocomplete_fields` attribute is a dictionary that defines the fields to be populated from the selected item in the dropdown. The key is the field name in form, and the value is the field name from the API call response.

```json
{
    "name": "name",
    "required": true,
    "label": "Name",
    "readonly": false,
    "listing": true,
    "type": "suggestion_dropdown",
    "suggestion_id_fieldname": "_id",
    "suggestion_desc_fieldname": "name",
    "filter_api_url": "user_ingredients",
    "filter_api_request_method": "GET",
    "filter_search_param_name": "name",
    "filter_search_other_param": {
        "like": "1",
        "user_id": "{CurrentUserId}"
    },
    "autocomplete_fields": {
        "calories_value": "calories_value",
        "calories_unit": "calories_unit",
        "serving_size": "serving_size",
        "serving_size_unit": "serving_size_unit",
        "brand_name": "brand_name",
        "observations": "observations"
    },
    "chatbot_popup": true,
    "aux_component": "ChatBotButton",
    "chatbot_prompt": "Give me the %s calories in KCAL including the serving size amount and serving size unit. Look first in my ingredients, if it's not there, look for it with the web_search Tool.",
    "google_popup": true,
    "google_prompt": "%s calories KCAL"
},
```

### Specific functions

Functions that extend the generic CRUD editor functionality from the frontend perspective. They're intended to be used before and after the database operations: read, write, delete, and validations.

Each specific function value is a lists (arrays) of ReactJS functions that will be executed in the order they are listed.

All the specific functions are all optional.

* **dbListPreRead**: Before read data from database in the listing. Good place for hidden filters.
    + Example:
```json
"dbListPreRead": [
    "UsersDbListPreRead"
],
```

* **dbListPostRead**: After read data from database in the listing. At the end of the list, the `timestampDbListPostRead` will be always appended to perform the Timestamp to Date convertion of `date` and `datetime-local` type fields.

* **dbPreRead**: Before read data from database in formData. If any error, shows the error message.

* **dbPostRead**: After read data from database in formData. If any error, shows the error message. At the end of the list, the `timestampDbPostRead` will be always appended to perform the Timestamp to Date convertion of `date` and `datetime-local` type fields.

* **dbPreValidations**: FormData field values validation before doing a Delete operation. If any error, prevents the database row to be deleted.
    + Example:
```json
"dbPreValidations": [
    "UsersValidations"
],
```

* **validations**: FormData field values validation before write to the database. If any error, prevents the database write and stays in FormData.
    + Example:
```json
"validations": [
    "UsersPasswordValidations"
]
```

* **dbPreWrite**: Before write to database, after a successfull validation. If any error, shows the error message, prevents the database write and stays in FormData.
    + Example:
```json
"dbPreWrite": [
    "UsersDbPreWrite"
],
```
At the end of the list, the `timestampDbPreWrite` will be appended by default to handle the timestamp assignment to `date` and `datetime-local` type fields. If `update_date` doesn't exist in the form, the current timestamp will be assigned to it.

* **dbPostWrite**: After a successful write to database. If any error, shows the error message and stays in FormData.
    + Example:
```json
"dbPostWrite": [
    "UsersDbPostWrite"
],
```

### Formulas

Formulas are used to calculate the fields' values from other fields.

Example: in a Order form with a 1 to many relationship with Order Lines, the `total` field could have the `totalCalcInOrderLine` in the **formula** attribute and the corresponding ReactJS component could be:

```jsx
export const totalCalcInOrderLine = () => {
    // Calculate the total price of the order lines by multiplying the price by the quantity
    const response = (parseFloat(document.getElementsByName('price')[0].value) * parseFloat(document.getElementsByName('quantity')[0].value)).toFixed(2);
    return response;
}
```

To calculate the form data page's `grand_total`, there must be a `dbPostWrite` specific function in the Order Lines child component, e.g.  `granTotalFromOrderLines` and the ReactJS componet could be: 

```jsx
const dbApiService = gs.dbService.dbApiService;
const genericFuncArrayDefaultValue = gs.genericEditorRfcSpecificFunc.genericFuncArrayDefaultValue;
const ACTION_DELETE = gs.generalConstants.ACTION_DELETE;
const ACTION_CREATE = gs.generalConstants.ACTION_CREATE;
const ACTION_UPDATE = gs.generalConstants.ACTION_UPDATE;

export const granTotalFromOrderLines = ({
    data,
    editor,
    action,
}) => {
    return new Promise((resolve, reject) => {
        let resp = genericFuncArrayDefaultValue(data);
        let grand_total = 0;
        const parentId = editor.parentData[editor.endpointKeyNames[0].parentElementName];
        let childFilter = {};
        childFilter[editor.endpointKeyNames[0].parameterName] = parentId;
        switch(action) {
            case ACTION_CREATE:
            case ACTION_UPDATE:
            case ACTION_DELETE:
                const db = new dbApiService({ url: editor.parentUrl });
                // Get the parent item data
                db.getOne({id: parentId}).then( 
                    data => {
                        if (!data['resultset']) {
                            resp.error = true;
                            resp.errorMsg = (resp.errorMsg === '' ? '' : '<br>') + 
                                `Cannot read Parent Table ID: ${parentId}`;
                        }
                        if (resp.error) {
                            reject(resp);
                        } else {
                            // Get the child items data
                            const db2 = new dbApiService({ url: editor.dbApiUrl });
                            db2.getAll(childFilter).then( 
                                data2 => {
                                    // Calculate the grand total summing the child items
                                    grand_total = data2['resultset'].reduce( (total, row) => {
                                        total += (row["quantity"] * row["price"]);
                                        return total;
                                    }, 0)
                                    // Update the parent item with the grand total
                                    let itemToSave = (data['resultset']);
                                    itemToSave["grand_total"] = grand_total.toFixed(2);
                                    delete itemToSave["_id"];
                                    db.updateRow(parentId, itemToSave).then(
                                        _ => {
                                            // Refresh the parent (main table) form data once the child items are updated in the database
                                            resp['otherData']['refresh'] = true;
                                            resolve(resp);
                                        },
                                        error => {
                                            resp.error = true;
                                            resp.errorMsg = error;
                                            reject(resp)
                                        }
                                    );
                                },
                                error => {
                                    resp.error = true;
                                    resp.errorMsg = error;
                                    reject(resp)
                                }
                            );
                        }
                    },
                    error => {
                        resp.error = true;
                        resp.errorMsg = error;
                        reject(resp)
                    }
                );
                break;
            default:
                resolve(resp);
        }
    });
}
```

## Backend Configuration

This configuration is used by the backend exclusively.

### Validation

The TypeScript interfaces to validate the backend JSON configurations are defined in [CrudEditorConfigInterface.ts](https://github.com/tomkat-cr/genericsuite-basecamp/blob/main/docs/code/configuration-guide/CrudEditorConfigInterface.ts) file (`BackendCrudEditorConfig`).

The Python classes to validate the backend JSON configurations are defined in [crud_editor_config_classes.py](https://github.com/tomkat-cr/genericsuite-basecamp/blob/main/docs/code/configuration-guide/crud_editor_config_classes.py) file (`BackendCrudEditorConfig`).

### Backend Configuration Attributes

* **table_name**: physical table name in the database.
    + Example:
```json
    "table_name": "users",
```

* **creation_pk_name**: column/attribute name in the database used as the primary key for the table during the creation process.
    + Example:
```json
    "creation_pk_name": "email",
```

* **projection_exclusion**: list of attributes to exclude from the projection.
    + Example:
```json
    "projection_exclusion": [
        "passcode"
    ],
```

* **email_verification**: list of attributes to be validated as email addresses.
    + Example:
```json
    "email_verification": [
        "email"
    ],
```

* **passwords**: list of attributes to be validated as passwords.
    + Example:
```json
    "passwords": [
        "passcode"
    ],
```

* **mandatory_fields**: list of attributes that must be present in the table.
    + Example:
```json
    "mandatory_fields": [
        "firstname",
        "lastname",
        "creation_date",
        "gender",
        "birthday",
        "email"
    ],
```

* **additional_query_params**: list of attributes to be used in the query operations other than the primary key.
    + Example:
```json
    "additional_query_params": [
        "email"
    ],
```

* **specific_function**: specific function to be executed before and after database operations.
    + Examples:
```json
    "specific_function": "delete_params_file"
```
```json
    "specific_function": "app_other_specific_function"
```

**IMPORTANT**: for non-standard specific functions like "delete_params_file", the function must be implemented in the backend:

```python
from genericsuite_ai.fastapilib.util.create_app import (
    create_app,
    create_handler
)

from app.config.config import Config

# Import the specific function
from app.specific_functions import app_other_specific_function


settings = Config()
app = create_app(
    app_name=f"{settings.APP_NAME.lower()}-backend", settings=settings)

# Register the specific function
app.custom_data['app_other_specific_function'] = app_other_specific_function

handler = create_handler(app)
```

## Examples

Let's see some examples of the configuration files using a hypothetical App [GenericSuite Example App](../../code/exampleapp/README.md) to track calories and create meal plans. The configuration files are located in the [exampleapp/apps/config_dbdef](../../code/exampleapp/apps/config_dbdef/README.md) directory.

### Directory Structure

```
exampleapp/apps/config_dbdef/
├── backend/
|   ├── ai_chatbot_conversations.json           # AI Chatbot conversations for the Chatbot UI
|   ├── app_main_menu.json                      # App main menu configuration
|   ├── clarifai_models.json                    # Clarifai AI models
|   ├── daily_meal_ingredients.json             # User's daily meal ingredients
|   ├── daily_meals.json                        # User's daily meal list
|   ├── dish_ingredients.json                   # User's dish ingredients
|   ├── dishes.json                             # User's dishes list
|   ├── endpoints.json                          # App backend API endpoints configuration
|   ├── food_moments.json                       # General food types (or moments) list
|   ├── general_config.json                     # App dynamic configuration parameters
|   ├── general_ingredients.json                # Global ingredients
|   ├── user_ingredients_all.json               # All user's ingredients
|   ├── user_ingredients.json                   # User's ingredients
|   ├── users_api_keys.json                     # User's API keys
|   ├── users_config.json                       # User's configuration parameters
|   ├── users_food_times.json                   # User's typical meal ingestion times
|   ├── users_profile.json                      # User's profile page
|   ├── users_user_history.json                 # User's data history (goals, weight, etc.)
|   ├── users.json                              # Users
├── frontend/
|   ├── ai_chatbot_conversations_complete.json  # AI Chatbot conversations for a CRUD editor
|   ├── ai_chatbot_conversations.json           # AI Chatbot conversations for the Chatbot UI
|   ├── app_constants.json                      # App general constants (billing plans, units, types, codes, gender, emails, urls, etc.)
|   ├── clarifai_models.json                    # Clarifai AI models
|   ├── daily_meal_ingredients.json             # User's daily meal ingredients
|   ├── daily_meals.json                        # User's daily meal list
|   ├── dish_ingredients.json                   # User's dish ingredients
|   ├── dishes.json                             # User's dishes list
|   ├── food_moments.json                       # General food types (or moments) list
|   ├── general_config.json                     # App dynamic configuration parameters
|   ├── general_constants.json                  # App general constants (true/false, yes/no, languages, genders, etc.)
|   ├── general_ingredients.json                # Global ingredients
|   ├── user_ingredients_all.json               # All user's ingredients
|   ├── user_ingredients.json                   # User's ingredients
|   ├── users_api_keys.json                     # User's API keys
|   ├── users_config.json                       # User's configuration parameters
|   ├── users_food_times.json                   # User's typical meal ingestion times
|   ├── users_profile.json                      # User's profile page
|   ├── users_user_history.json                 # User's data history (goals, weight, etc.)
|   ├── users.json                              # Users
├── .gitignore
├── CHANGELOG.md
├── package.json
├── README.md
```

### backend/ai_chatbot_conversations.json

AI Chatbot conversations for the Chatbot UI

```json
{
    "table_name": "ai_chatbot_conversations",
    "creation_pk_name": "_id",
    "additional_query_params": [
        "_id"
    ]
}
```

### backend/app_main_menu.json

App main menu configuration

```json
[
    {
        "title": "Home",
        "location": "top_menu",
        "type": "nav_link",
        "path": "/",
        "element": "HomePage",
        "hard_prefix": false,
        "reload": true
    },
    {
        "title": "Admin",
        "location": "top_menu",
        "type": "nav_dropdown",
        "sec_group": "admin",
        "sub_menu_options": [
            {
                "type": "editor",
                "sec_group": "admin",
                "title": "Users",
                "element": "Users_EditorData"
            },
            {
                "type": "editor",
                "sec_group": "admin",
                "title": "Meal Types",
                "element": "FoodMoments_EditorData"
            },
            {
                "type": "editor",
                "sec_group": "admin",
                "title": "General Ingredients",
                "element": "GeneralIngredients_EditorData"
            },
            {
                "type": "editor",
                "sec_group": "admin",
                "title": "General Config",
                "element": "GeneralConfig_EditorData"
            },
            {
                "type": "editor",
                "sec_group": "admin",
                "title": "Clarifai Models",
                "element": "ClarifaiModels_EditorData"
            }
        ]
    },
    {
        "title": "Foods",
        "location": "top_menu",
        "type": "nav_dropdown",
        "sec_group": "users",
        "sub_menu_options": [
            {
                "type": "editor",
                "sec_group": "users",
                "title": "Ingredients",
                "element": "UserIngredients_EditorData"
            },
            {
                "type": "editor",
                "sec_group": "users",
                "title": "Dishes",
                "element": "Dishes_EditorData"
            },
            {
                "type": "editor",
                "sec_group": "users",
                "title": "Daily Meals",
                "element": "DailyMeals_EditorData"
            }
        ]
    },
    {
        "title": "ExampleApp Bot",
        "location": "top_menu",
        "type": "nav_link",
        "sec_group": "users",
        "path": "/chatbot",
        "element": "Chatbot"
    },
    {
        "title": "User Menu",
        "location": "hamburger",
        "sub_menu_options": [
            {
                "title": "Profile",
                "path": "/profile",
                "element": "UserProfileEditor"
            },
            {
                "title": "Preferences",
                "path": "#preferences",
                "element": "PreferencesEditor"
            },
            {
                "title": "About",
                "on_click": "|about|"
            },
            {
                "title": "Logout",
                "path": "/logout",
                "on_click": "logout"
            }
        ]
    },
    {
        "title": "Other Routes",
        "sub_menu_options": [
            {
                "title": "Absolut Home",
                "path": "/",
                "element": "HomePage",
                "get_prefix": false
            },
            {
                "title": "About body",
                "path": "/about_body",
                "element": "AboutBody",
                "get_prefix": false
            }
        ]
    }
]
```

### backend/clarifai_models.json

Clarifai AI models

```json
{
    "table_name": "clarifai_models",
    "creation_pk_name": "model_name",
    "additional_query_params": [
        "model_name"
    ]
}
```

### backend/daily_meal_ingredients.json

User's daily meal ingredients

```json
{
    "table_name": "daily_meals"
}
```

### backend/daily_meals.json

User's daily meal list

```json
{
    "table_name": "daily_meals"
}
```

### backend/dish_ingredients.json

User's dish ingredients

```json
{
    "table_name": "user_ingredients",
    "notes": "'dishes' are 'user_ingredients' with type 'D'"
}
```

### backend/dishes.json

User's dishes list

```json
{
    "table_name": "user_ingredients",
    "notes": "'dishes' are 'user_ingredients' with type 'D'",
    "creation_pk_name": "name",
    "additional_query_params": [
        "name"
    ]
}
```

### backend/endpoints.json

App backend API endpoints configuration

```json
[
    {
        "name": "food_moments",
        "url_prefix": "food_moments",
        "routes": [
            {
                "endpoint": "/",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "handler_type": "GenericEndpointHelper",
                "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
                "params": {
                    "json_file": "food_moments"
                }
            }
        ]
    },
    {
        "name": "general_ingredients",
        "url_prefix": "general_ingredients",
        "routes": [
            {
                "endpoint": "/",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "handler_type": "GenericEndpointHelper",
                "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
                "params": {
                    "json_file": "general_ingredients"
                }
            }
        ]
    },
    {
        "name": "user_ingredients",
        "url_prefix": "user_ingredients",
        "routes": [
            {
                "endpoint": "/",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "handler_type": "GenericEndpointHelper",
                "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
                "params": {
                    "json_file": "user_ingredients"
                }
            }
        ]
    },
    {
        "name": "user_ingredients_all",
        "url_prefix": "user_ingredients_all",
        "routes": [
            {
                "endpoint": "/",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "handler_type": "GenericEndpointHelper",
                "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
                "params": {
                    "json_file": "user_ingredients_all"
                }
            }
        ]
    },
    {
        "name": "dishes",
        "url_prefix": "dishes",
        "routes": [
            {
                "endpoint": "/",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "handler_type": "GenericEndpointHelper",
                "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
                "params": {
                    "json_file": "dishes"
                }
            }
        ]
    },
    {
        "name": "dish_ingredients",
        "url_prefix": "dish_ingredients",
        "routes": [
            {
                "endpoint": "/",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "handler_type": "GenericEndpointHelper",
                "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
                "params": {
                    "json_file": "dish_ingredients"
                }
            }
        ]
    },
    {
        "name": "daily_meals",
        "url_prefix": "daily_meals",
        "routes": [
            {
                "endpoint": "/",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "handler_type": "GenericEndpointHelper",
                "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
                "params": {
                    "json_file": "daily_meals"
                }
            }
        ]
    },
    {
        "name": "daily_meal_ingredients",
        "url_prefix": "daily_meal_ingredients",
        "routes": [
            {
                "endpoint": "/",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "handler_type": "GenericEndpointHelper",
                "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
                "params": {
                    "json_file": "daily_meal_ingredients"
                }
            }
        ]
    },
    {
        "name": "ai_chatbot_conversations",
        "url_prefix": "ai_chatbot_conversations",
        "routes": [
            {
                "endpoint": "/",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "handler_type": "GenericEndpointHelper",
                "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
                "params": {
                    "json_file": "ai_chatbot_conversations"
                }
            }
        ]
    },
    {
        "name": "general_config",
        "url_prefix": "general_config",
        "routes": [
            {
                "endpoint": "/",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "handler_type": "GenericEndpointHelper",
                "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
                "params": {
                    "json_file": "general_config"
                }
            }
        ]
    },
    {
        "name": "users",
        "url_prefix": "users",
        "routes": [
            {
                "endpoint": "/",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "handler_type": "GenericEndpointHelper",
                "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
                "params": {
                    "json_file": "users"
                }
            }
        ]
    },
    {
        "name": "users_config",
        "url_prefix": "users_config",
        "routes": [
            {
                "endpoint": "/",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "handler_type": "GenericEndpointHelper",
                "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
                "params": {
                    "json_file": "users_config"
                }
            }
        ]
    },
    {
        "name": "users_food_times",
        "url_prefix": "users_food_times",
        "routes": [
            {
                "endpoint": "/",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "handler_type": "GenericEndpointHelper",
                "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
                "params": {
                    "json_file": "users_food_times"
                }
            }
        ]
    },
    {
        "name": "users_user_history",
        "url_prefix": "users_user_history",
        "routes": [
            {
                "endpoint": "/",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "handler_type": "GenericEndpointHelper",
                "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
                "params": {
                    "json_file": "users_user_history"
                }
            }
        ]
    },
    {
        "name": "users_api_keys",
        "url_prefix": "users_api_keys",
        "routes": [
            {
                "endpoint": "/",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "handler_type": "GenericEndpointHelper",
                "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
                "params": {
                    "json_file": "users_api_keys"
                }
            }
        ]
    }, 
    {
        "name": "clarifai_models",
        "url_prefix": "clarifai_models",
        "routes": [
            {
                "endpoint": "/",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "handler_type": "GenericEndpointHelper",
                "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
                "params": {
                    "json_file": "clarifai_models"
                }
            }
        ]
    }
]
```

### backend/food_moments.json

General food types (or moments) list

```json
{
    "table_name": "food_moments",
    "creation_pk_name": "name",
    "additional_query_params": [
        "name"
    ]
}
```

### backend/general_config.json

App dynamic configuration parameters

```json
{
    "table_name": "general_config",
    "creation_pk_name": "config_name",
    "additional_query_params": [
        "config_name"
    ],
    "specific_function": "delete_params_file"
}
```

### backend/general_ingredients.json

Global ingredients

```json
{
    "table_name": "general_ingredients",
    "creation_pk_name": "name",
    "additional_query_params": [
        "name"
    ]
}
```

### backend/user_ingredients_all.json

All user's ingredients

```json
{
    "table_name": "user_ingredients",
    "creation_pk_name": "name",
    "additional_query_params": [
        "name"
    ]
}
```

### backend/user_ingredients.json

User's ingredients

```json
{
    "table_name": "user_ingredients",
    "creation_pk_name": "name",
    "additional_query_params": [
        "name"
    ]
}
```

### backend/users_api_keys.json

User's API keys

```json
{
    "table_name": "users_api_keys",
    "specific_function": "delete_params_file"
}
```

### backend/users_config.json

User's configuration parameters

```json
{
    "table_name": "users",
    "specific_function": "delete_params_file"
}
```

### backend/users_food_times.json

User's typical meal ingestion times

```json
{
    "table_name": "users"
}
```

### backend/users_profile.json

User's profile page

```json
{
    "table_name": "users",
    "creation_pk_name": "email",
    "projection_exclusion": [
        "passcode"
    ],
    "email_verification": [
        "email"
    ],
    "passwords": [
        "passcode"
    ],
    "mandatory_fields": [
        "firstname",
        "lastname",
        "creation_date",
        "gender",
        "birthday",
        "email",
        "height",
        "height_unit",
        "weight",
        "weight_unit",
        "training_days",
        "training_hour"
    ],
    "additional_query_params": [
        "email"
    ],
    "specific_function": "delete_params_file"
}
```

### backend/users_user_history.json

User's data history (goals, weight, etc.)

```json
{
    "table_name": "users"
}
```

### backend/users.json

Users

```json
{
    "table_name": "users",
    "creation_pk_name": "email",
    "projection_exclusion": [
        "passcode"
    ],
    "email_verification": [
        "email"
    ],
    "passwords": [
        "passcode"
    ],
    "mandatory_fields": [
        "firstname",
        "lastname",
        "creation_date",
        "gender",
        "birthday",
        "email"
    ],
    "additional_query_params": [
        "email"
    ]
}
```

### frontend/ai_chatbot_conversations_complete.json

AI Chatbot conversations for a CRUD editor

```json
{
    "table_name": "ai_chatbot_conversations",
    "creation_pk_name": "_id",
    "additional_query_params": [
        "_id"
    ],
    "baseUrl": "ai_chatbot_conversations",
    "title": "ExampleApp Bot Conversations",
    "name": "ExampleApp Bot Conversation",
    "component": "ExampleApp Bot Conversations",
    "dbApiUrl": "ai_chatbot_conversations",
    "mandatoryFilters": {
        "user_id": "{CurrentUserId}"
    },
    "defaultOrder": "update_date|desc",
    "fieldElements": [
        {
            "name": "id",
            "label": "ID",
            "type": "_id",
            "listing": true
        },
        {
            "name": "user_id",
            "label": "User ID",
            "type": "text",
            "listing": true
        },
        {
            "name": "title",
            "label": "Title",
            "type": "text",
            "listing": true
        },
        {
            "name": "creation_date",
            "required": true,
            "label": "Created",
            "type": "datetime-local",
            "listing": true
        },
        {
            "name": "update_date",
            "required": true,
            "label": "Last update",
            "type": "datetime-local",
            "listing": true
        },
        {
            "name": "messages",
            "required": true,
            "label": "Messages",
            "type": "array",
            "listing": true
        }
    ]
}
```

### frontend/ai_chatbot_conversations.json

AI Chatbot conversations for the Chatbot UI

```json
{
    "baseUrl": "ai_chatbot_conversations",
    "title": "ExampleApp Bot Conversations",
    "name": "ExampleApp Bot Conversation",
    "component": "ExampleApp Bot Conversations",
    "dbApiUrl": "ai_chatbot_conversations",
    "mandatoryFilters": {
        "user_id": "{CurrentUserId}"
    },
    "defaultOrder": "update_date|desc",
    "fieldElements": [
        {
            "name": "id",
            "required": true,
            "label": "ID",
            "type": "_id",
            "readonly": true,
            "hidden": true
        },
        {
            "name": "user_id",
            "required": true,
            "label": "User ID",
            "type": "text",
            "readonly": true,
            "hidden": true
        },
        {
            "name": "title",
            "required": true,
            "label": "Title",
            "type": "text",
            "readonly": true,
            "listing": true
        },
        {
            "name": "creation_date",
            "required": true,
            "label": "Created",
            "type": "datetime-local",
            "readonly": true,
            "hidden": false,
            "default_value": "current_timestamp",
            "listing": true
        },
        {
            "name": "update_date",
            "required": true,
            "label": "Last update",
            "type": "datetime-local",
            "readonly": true,
            "hidden": false,
            "default_value": "current_timestamp",
            "listing": true
        },
        {
            "name": "messages",
            "required": true,
            "label": "Messages",
            "type": "array",
            "readonly": true,
            "listing": false
        }
    ]
}
```

### frontend/app_constants.json

App general constants (billing plans, units, types, codes, gender, emails, urls, etc.)

```json
{
    "WEIGHT_UNITS": {
        "kg": "Kg",
        "lb": "Pounds"
    },
    "HEIGHT_UNITS": {
        "m": "Meters",
        "i": "Inches"
    },
    "GENDERS": {
        "m": "Male",
        "f": "Female"
    },
    "CALORIE_UNITS": {
        "kcal": "Calories (KCAL)",
        "kj": "KJoules (kj)"
    },
    "SERVING_SIZE_UNITS": {
        "g": "Grams (g)",
        "u": "Unit",
        "tsp": "Tea spoon",
        "tablespoon": "Table spoon",
        "bowl": "Bowl (300 ml)",
        "cup": "Cup (200 ml)",
        "scup": "Small Cup (150 ml)",
        "ml": "Milliliters (ml)",
        "mg": "Milligrams (mg)",
        "ug": "Micro grams (ug)",
        "oz": "Ounce (oz)",
        "lb": "Pound (lb)",
        "iu": "International units (iu)",
        "mlt": "Mass, length, time (mlt)"
    },
    "INGREDIENT_TYPE": {
        "I": "Ingredient",
        "D": "Dish"
    },
    "GOAL_CODES": {
        "-20-DEFAULT": "Lose weight:",
        "-10": "-10% slower but safer descent (recommended to preserve muscle mass & performance)",
        "-20": "-20% want weight loss to be somewhat faster",
        "-30": "-30% urgency to lose weight quickly or suffer from obesity",
        "+20-DEFAULT": "Gain weight:",
        "+10": "+10% have a tendency to gain weight or have been training for a long time and want to gain muscle mass",
        "+15": "+15% want to gain a little more weight",
        "+20": "+20% for ectomorphs or hardgainers"
    },
    "BILLING_PLANS": {
        "free": "Free",
        "basic": "Basic",
        "premium": "Premium"
    },
    "ERROR_MESSAGES": {
        "ACCOUNT_INACTIVE": "User account inactive [L5]. To activate your account, please contact support@exampleapp.com"
    },
    "APP_EMAILS": {
        "SUPPORT_EMAIL": "support@exampleapp.com",
        "INFO_EMAIL": "info@exampleapp.com"
    },
    "APP_VALID_URLS": {
        "APP_DOMAIN": "exampleapp.com",
        "APP_WEBSITE": "https://www.exampleapp.com"
    },
    "AI_PROMPT_TEMPLATES": {
        "ASSISTANT_YOU_ARE": "{assistant_name}. You are part of ExampleApp, an App that allows Humans to record their favorite food ingredients, recipes, and daily meals, track calorie consumption, and create calorie-deficit menus based on affordable and preferred ingredients and recipes. You provide AI-powered experiences to Humans using large language models, speech-to-text, text-to-image, and image-to-text technologies, enabling them to interact via voice, text, or image uploads.",
        "BOTTOM_LINE": "If the calorie information couldn't be retrieved from the FDA database, search it on the Internet, and if it fails too, deduce it from your model."
    }
}
```

### frontend/clarifai_models.json

Clarifai AI models

```json
{
    "baseUrl": "clarifai_models",
    "title": "Clarifai Models",
    "name": "Clarifai Model Configuration",
    "component": "ClarifaiModels",
    "dbApiUrl": "clarifai_models",
    "defaultOrder": "model_name|asc",
    "fieldElements": [
        {
            "name": "id",
            "required": true,
            "label": "ID",
            "type": "_id",
            "readonly": true
        },
        {
            "name": "model_name",
            "required": true,
            "label": "Name",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "active",
            "required": true,
            "label": "Active",
            "type": "select",
            "select_elements": "TRUE_FALSE",
            "readonly": false,
            "hidden": false,
            "default_value": "1",
            "listing": true
        },
        {
            "name": "user_id",
            "required": true,
            "label": "User ID",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "app_id",
            "required": true,
            "label": "App ID",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "model_id",
            "required": true,
            "label": "Model ID",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "model_version_id",
            "required": true,
            "label": "Model Version ID",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "model_url",
            "required": false,
            "label": "Model URL",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "notes",
            "required": false,
            "label": "Notes",
            "type": "text",
            "readonly": false,
            "listing": true
        }
    ]
}
```

### frontend/daily_meal_ingredients.json

User's daily meal ingredients

```json
{
    "baseUrl": "daily_meal_ingredients",
    "title": "Meal Ingredients",
    "name": "Meal Ingredient",
    "dbApiUrl": "daily_meal_ingredients",
    "component": "DailyMealIngredients",
    "type": "child_listing",
    "subType": "array",
    "array_name": "meal_ingredients",
    "parentUrl": "daily_meals",
    "endpointKeyNames": [
        {
            "parameterName": "daily_meal_id",
            "parentElementName": "id"
        }
    ],
    "primaryKeyName": "id",
    "allow_duplicates": true,
    "fieldElements": [
        {
            "name": "id",
            "required": false,
            "label": "ID",
            "type": "text",
            "readonly": true,
            "hidden": true,
            "listing": false,
            "uuid_generator": true
        },
        {
            "name": "meal_type",
            "label": "Type",
            "required": true,
            "listing": true,
            "type": "suggestion_dropdown",
            "suggestion_id_fieldname": "_id",
            "suggestion_desc_fieldname": "name",
            "filter_api_url": "food_moments",
            "filter_api_request_method": "GET",
            "filter_search_param_name": "name",
            "filter_search_other_param": {
                "like": "1"
            }
        },            
        {
            "name": "name",
            "required": true,
            "label": "Name",
            "readonly": false,
            "listing": true,
            "type": "suggestion_dropdown",
            "suggestion_id_fieldname": "_id",
            "suggestion_desc_fieldname": "name",
            "filter_api_url": "user_ingredients_all",
            "filter_api_request_method": "GET",
            "filter_search_param_name": "name",
            "filter_search_other_param": {
                "like": "1",
                "user_id": "{CurrentUserId}"
            },
            "autocomplete_fields": {
                "calories_value": "calories_value",
                "calories_unit": "calories_unit",
                "serving_size": "serving_size",
                "serving_size_unit": "serving_size_unit",
                "brand_name": "brand_name",
                "observations": "observations"
            },
            "chatbot_popup": true,
            "aux_component": "ChatBotButton",
            "chatbot_prompt": "Give me the %s calories in KCAL including the serving size amount and serving size unit. Look first in my ingredients, if it's not there, look for it with the web_search Tool.",
            "google_popup": true,
            "google_prompt": "%s calories KCAL"
        },
        {
            "name": "calories_value",
            "required": true,
            "label": "Calories",
            "type": "number",
            "readonly": false,
            "listing": true
        },
        {
            "name": "calories_unit",
            "required": true,
            "label": "Calories Unit",
            "type": "select",
            "select_elements": "CALORIE_UNITS",
            "readonly": false,
            "listing": true,
            "default_value": "kcal"
        },
        {
            "name": "serving_size",
            "required": true,
            "label": "Serving size",
            "type": "number",
            "readonly": false,
            "listing": true
        },
        {
            "name": "serving_size_unit",
            "required": true,
            "label": "Serving size unit",
            "type": "select",
            "select_elements": "SERVING_SIZE_UNITS",
            "readonly": false,
            "listing": true,
            "default_value": "g"
        },
        {
            "name": "quantity",
            "required": true,
            "label": "Qty.",
            "type": "number",
            "min": "0",
            "max": "9999",
            "readonly": false,
            "listing": true
        },
        {
            "name": "total_calories",
            "label": "Total",
            "type": "number",
            "readonly": true,
            "listing": true,
            "formula": "totalCaloriesCalcInDailyMealIngredients"
        },
        {
            "name": "brand_name",
            "required": false,
            "label": "Brand Name",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "observations",
            "required": false,
            "label": "Observations",
            "type": "textarea",
            "readonly": false,
            "listing": true
        }
    ],
    "dbPostWrite": [
        "DailyMealIngredientsDbPostWrite"
    ]
}
```

### frontend/daily_meals.json

User's daily meal list

```json
{
    "baseUrl": "daily_meals",
    "title": "Daily Meals",
    "name": "Daily Meal",
    "component": "DailyMeals",
    "dbApiUrl": "daily_meals",
    "mandatoryFilters": {
        "user_id": "{CurrentUserId}"
    },
    "createReenter": true,
    "defaultOrder": "meal_date|desc",
    "fieldElements": [
        {
            "name": "id",
            "required": true,
            "label": "ID",
            "type": "_id",
            "readonly": true,
            "hidden": true
        },
        {
            "name": "user_id",
            "required": true,
            "label": "User ID",
            "type": "text",
            "readonly": true,
            "hidden": true
        },
        {
            "name": "meal_date",
            "required": true,
            "label": "Date",
            "type": "date",
            "readonly": false,
            "listing": true
        },
        {
            "name": "total_calories",
            "label": "Total Calories",
            "type": "number",
            "readonly": true,
            "listing": true,
            "component": "UserDailyCaloriesAndCondition"
        },
        {
            "name": "minimun_daily_calories",
            "label": "Daily Calorie Goal",
            "type": "component",
            "component": "UserMinimumDailyCalories",
            "readonly": true,
            "listing": false
        },
        {
            "name": "observations",
            "required": false,
            "label": "Observations",
            "type": "textarea",
            "readonly": false,
            "listing": true
        }
    ],
    "childComponents": [
        "DailyMealIngredients"
    ]
}
```

### frontend/dish_ingredients.json

User's dish ingredients

```json
{
    "baseUrl": "dish_ingredients",
    "title": "Dish Ingredients",
    "name": "Dish Ingredient",
    "dbApiUrl": "dish_ingredients",
    "component": "DishIngredients",
    "type": "child_listing",
    "subType": "array",
    "array_name": "dish_ingredients",
    "parentUrl": "dishes",
    "endpointKeyNames": [
        {
            "parameterName": "dish_id",
            "parentElementName": "id"
        }
    ],
    "primaryKeyName": "id",
    "allow_duplicates": true,
    "fieldElements": [
        {
            "name": "id",
            "required": false,
            "label": "ID",
            "type": "text",
            "readonly": true,
            "hidden": true,
            "listing": false,
            "uuid_generator": true
        },
        {
            "name": "name",
            "required": true,
            "label": "Name",
            "readonly": false,
            "listing": true,
            "type": "suggestion_dropdown",
            "suggestion_id_fieldname": "_id",
            "suggestion_desc_fieldname": "name",
            "filter_api_url": "user_ingredients",
            "filter_api_request_method": "GET",
            "filter_search_param_name": "name",
            "filter_search_other_param": {
                "like": "1",
                "user_id": "{CurrentUserId}"
            },
            "autocomplete_fields": {
                "calories_value": "calories_value",
                "calories_unit": "calories_unit",
                "serving_size": "serving_size",
                "serving_size_unit": "serving_size_unit",
                "brand_name": "brand_name",
                "observations": "observations"
            },
            "chatbot_popup": true,
            "aux_component": "ChatBotButton",
            "chatbot_prompt": "Give me the %s calories in KCAL including the serving size amount and serving size unit. Look first in my ingredients, if it's not there, look for it with the web_search Tool.",
            "google_popup": true,
            "google_prompt": "%s calories KCAL"
        },
        {
            "name": "calories_value",
            "required": true,
            "label": "Calories",
            "type": "number",
            "readonly": false,
            "listing": true
        },
        {
            "name": "calories_unit",
            "required": true,
            "label": "Calories Unit",
            "type": "select",
            "select_elements": "CALORIE_UNITS",
            "readonly": false,
            "listing": true,
            "default_value": "kcal"
        },
        {
            "name": "serving_size",
            "required": true,
            "label": "Serving size",
            "type": "number",
            "readonly": false,
            "listing": true
        },
        {
            "name": "serving_size_unit",
            "required": true,
            "label": "Serving size unit",
            "type": "select",
            "select_elements": "SERVING_SIZE_UNITS",
            "readonly": false,
            "listing": true,
            "default_value": "g"
        },
        {
            "name": "quantity",
            "required": true,
            "label": "Qty.",
            "type": "number",
            "min": "0",
            "max": "9999",
            "readonly": false,
            "listing": true
        },
        {
            "name": "total_calories",
            "label": "Total",
            "type": "number",
            "readonly": true,
            "listing": true,
            "formula": "totalCaloriesCalcInDishesIngredients"
        },
        {
            "name": "brand_name",
            "required": false,
            "label": "Brand Name",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "observations",
            "required": false,
            "label": "Observations",
            "type": "textarea",
            "readonly": false,
            "listing": true
        }
    ],
    "dbPostWrite": [
        "DishIngredientsDbPostWrite"
    ]
}
```

### frontend/dishes.json

User's dishes list

```json
{
    "baseUrl": "dishes",
    "title": "Dishes",
    "name": "Dish",
    "component": "Dishes",
    "dbApiUrl": "dishes",
    "mandatoryFilters": {
        "user_id": "{CurrentUserId}",
        "type": "D"
    },
    "fieldElements": [
        {
            "name": "id",
            "required": true,
            "label": "ID",
            "type": "_id",
            "readonly": true,
            "hidden": true
        },
        {
            "name": "user_id",
            "required": true,
            "label": "User ID",
            "type": "text",
            "readonly": true,
            "hidden": true
        },
        {
            "name": "type",
            "required": true,
            "label": "Type",
            "type": "select",
            "select_elements": "INGREDIENT_TYPE",
            "readonly": true,
            "hidden": false,
            "default_value": "D"
        },
        {
            "name": "name",
            "required": true,
            "label": "Name",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "calories_value",
            "required": true,
            "label": "Calories",
            "type": "number",
            "readonly": false,
            "listing": true,
            "default_value": "0"
        },
        {
            "name": "calories_unit",
            "required": true,
            "label": "Calories Unit",
            "type": "select",
            "select_elements": "CALORIE_UNITS",
            "readonly": false,
            "listing": true,
            "default_value": "kcal"
        },
        {
            "name": "serving_size",
            "required": true,
            "label": "Serving size",
            "type": "number",
            "readonly": false,
            "listing": true,
            "default_value": "1"
        },
        {
            "name": "serving_size_unit",
            "required": true,
            "label": "Serving size unit",
            "type": "select",
            "select_elements": "SERVING_SIZE_UNITS",
            "readonly": false,
            "listing": true,
            "default_value": "u" 
        },
        {
            "name": "brand_name",
            "required": false,
            "label": "Brand Name",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "observations",
            "required": false,
            "label": "Observations",
            "type": "textarea",
            "readonly": false,
            "listing": true
        },
        {
            "name": "creation_date",
            "required": true,
            "label": "Created",
            "type": "datetime-local",
            "readonly": true,
            "hidden": false,
            "default_value": "current_timestamp",
            "listing": true
        },
        {
            "name": "update_date",
            "required": true,
            "label": "Last update",
            "type": "datetime-local",
            "readonly": true,
            "hidden": false,
            "default_value": "current_timestamp",
            "listing": false
        }
    ],
    "childComponents": [
        "DishIngredients"
    ],
    "dbPreValidations": [
        "UserIngredientsValidations"
    ]
}
```

### frontend/food_moments.json

General food types (or moments) list

```json
{
    "baseUrl": "food_moments",
    "title": "Food Moments",
    "name": "Food Moment",
    "component": "FoodMoments",
    "dbApiUrl": "food_moments",
    "fieldElements": [
        {
            "name": "id",
            "required": true,
            "label": "ID",
            "type": "_id",
            "readonly": true
        },
        {
            "name": "name",
            "required": true,
            "label": "Name",
            "type": "text",
            "readonly": false,
            "listing": true
        }
    ],
    "dbPreValidations": [
        "FoodMomentsValidations"
    ]
}
```

### frontend/general_config.json

App dynamic configuration parameters

```json
{
    "baseUrl": "general_config",
    "title": "Configuration Parameters",
    "name": "Configuration Parameter",
    "component": "GeneralConfig",
    "dbApiUrl": "general_config",
    "defaultOrder": "config_name|asc",
    "fieldElements": [
        {
            "name": "id",
            "required": true,
            "label": "ID",
            "type": "_id",
            "readonly": true
        },
        {
            "name": "config_name",
            "required": true,
            "label": "Name",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "active",
            "required": true,
            "label": "Active",
            "type": "select",
            "select_elements": "TRUE_FALSE",
            "readonly": false,
            "hidden": false,
            "default_value": "1",
            "listing": true
        },
        {
            "name": "config_value",
            "required": true,
            "label": "Value",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "notes",
            "required": true,
            "label": "Notes",
            "type": "text",
            "readonly": false,
            "listing": true
        }
    ]
}
```

### frontend/general_constants.json

App general constants (true/false, yes/no, languages, genders, etc.)

```json
{
    "TRUE_FALSE": {
        "1": "Yes",
        "0": "No"
    },
    "YES_NO": {
        "y": "Yes",
        "n": "No"
    },
    "LANGUAGES": {
        "en": "English",
        "es": "Español"
    },
    "GENDERS": {
        "m": "Male",
        "f": "Female"
    }
}
```

### frontend/general_ingredients.json

Global ingredients

```json
{
    "baseUrl": "general_ingredients",
    "title": "Ingredients (general)",
    "name": "Ingredient",
    "component": "GeneralIngredients",
    "dbApiUrl": "general_ingredients",
    "fieldElements": [
        {
            "name": "id",
            "required": true,
            "label": "ID",
            "type": "_id",
            "readonly": true
        },
        {
            "name": "name",
            "required": true,
            "label": "Name",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "calories_value",
            "required": true,
            "label": "Calories",
            "type": "number",
            "readonly": false,
            "listing": true
        },
        {
            "name": "calories_unit",
            "required": true,
            "label": "Calories Unit",
            "type": "select",
            "select_elements": "CALORIE_UNITS",
            "readonly": false,
            "listing": true
        },
        {
            "name": "serving_size",
            "required": true,
            "label": "Serving size",
            "type": "number",
            "readonly": false,
            "listing": true
        },
        {
            "name": "serving_size_unit",
            "required": true,
            "label": "Serving size unit",
            "type": "select",
            "select_elements": "SERVING_SIZE_UNITS",
            "readonly": false,
            "listing": true
        },
        {
            "name": "brand_name",
            "required": false,
            "label": "Brand Name",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "other_names",
            "required": false,
            "label": "Other Names",
            "type": "text",
            "readonly": false,
            "listing": true
        }
    ],
    "dbPreValidations": [
        "GeneralIngredientsValidations"
    ]
}
```

### frontend/user_ingredients_all.json

All user's ingredients

```json
{
    "baseUrl": "user_ingredients",
    "title": "Ingredients for Suggestions",
    "name": "Ingredient",
    "component": "UserIngredients",
    "dbApiUrl": "user_ingredients",
    "mandatoryFilters": {
        "user_id": "{CurrentUserId}"
    },
    "fieldElements": [
        {
            "name": "id",
            "required": true,
            "label": "ID",
            "type": "_id",
            "readonly": true,
            "hidden": true
        },
        {
            "name": "user_id",
            "required": true,
            "label": "User ID",
            "type": "text",
            "readonly": true,
            "hidden": true
        },
        {
            "name": "name",
            "required": true,
            "label": "Name",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "calories_value",
            "required": true,
            "label": "Calories",
            "type": "number",
            "readonly": false,
            "listing": true
        },
        {
            "name": "calories_unit",
            "required": true,
            "label": "Calories Unit",
            "type": "select",
            "select_elements": "CALORIE_UNITS",
            "readonly": false,
            "listing": true,
            "default_value": "kcal" 
        },
        {
            "name": "serving_size",
            "required": true,
            "label": "Serving size",
            "type": "number",
            "readonly": false,
            "listing": true
        },
        {
            "name": "serving_size_unit",
            "required": true,
            "label": "Serving size unit",
            "type": "select",
            "select_elements": "SERVING_SIZE_UNITS",
            "readonly": false,
            "listing": true,
            "default_value": "g" 
        },
        {
            "name": "brand_name",
            "required": false,
            "label": "Brand Name",
            "type": "text",
            "readonly": false,
            "listing": true
        }
    ]
}
```

### frontend/user_ingredients.json

User's ingredients

```json
{
    "baseUrl": "user_ingredients",
    "title": "Ingredients",
    "name": "Ingredient",
    "component": "UserIngredients",
    "dbApiUrl": "user_ingredients",
    "mandatoryFilters": {
        "user_id": "{CurrentUserId}",
        "type": "I"
    },
    "defaultOrder": "name",
    "fieldElements": [
        {
            "name": "id",
            "required": true,
            "label": "ID",
            "type": "_id",
            "readonly": true,
            "hidden": true
        },
        {
            "name": "user_id",
            "required": true,
            "label": "User ID",
            "type": "text",
            "readonly": true,
            "hidden": true
        },
        {
            "name": "type",
            "required": true,
            "label": "Type",
            "type": "select",
            "select_elements": "INGREDIENT_TYPE",
            "readonly": true,
            "hidden": false,
            "default_value": "I"
        },
        {
            "name": "name",
            "required": true,
            "label": "Name",
            "type": "suggestion_dropdown",
            "readonly": false,
            "listing": true,
            "suggestion_id_fieldname": "id",
            "suggestion_desc_fieldname": "description",
            "suggestion_name_fieldname": "food_name",
            "filter_api_url": "fda_food_query",
            "filter_search_param_name": "food_name",
            "filter_search_other_param": {
                "autocomplete": "1"
            },
            "autocomplete_fields": {
                "calories_value": "calories_value",
                "calories_unit": "calories_unit",
                "serving_size": "serving_size",
                "serving_size_unit": "serving_size_unit",
                "brand_name": "brand_name"
            },
            "chatbot_popup": true,
            "aux_component": "ChatBotButton",
            "chatbot_prompt": "Give me the %s calories in KCAL including the serving size amount and serving size unit. Look first in thr FDA API, if it's not there, look for it with the web_search Tool.",
            "google_popup": true,
            "google_prompt": "%s calories KCAL"
        },
        {
            "name": "calories_value",
            "required": true,
            "label": "Calories",
            "type": "number",
            "readonly": false,
            "listing": true
        },
        {
            "name": "calories_unit",
            "required": true,
            "label": "Calories Unit",
            "type": "select",
            "select_elements": "CALORIE_UNITS",
            "readonly": false,
            "listing": true,
            "default_value": "kcal" 
        },
        {
            "name": "serving_size",
            "required": true,
            "label": "Serving size",
            "type": "number",
            "readonly": false,
            "listing": true
        },
        {
            "name": "serving_size_unit",
            "required": true,
            "label": "Serving size unit",
            "type": "select",
            "select_elements": "SERVING_SIZE_UNITS",
            "readonly": false,
            "listing": true,
            "default_value": "g" 
        },
        {
            "name": "brand_name",
            "required": false,
            "label": "Brand Name",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "observations",
            "required": false,
            "label": "Observations",
            "type": "textarea",
            "readonly": false,
            "listing": true
        },
        {
            "name": "creation_date",
            "required": true,
            "label": "Created",
            "type": "datetime-local",
            "readonly": true,
            "hidden": false,
            "default_value": "current_timestamp",
            "listing": true
        },
        {
            "name": "update_date",
            "required": true,
            "label": "Last update",
            "type": "datetime-local",
            "readonly": true,
            "hidden": false,
            "default_value": "current_timestamp",
            "listing": false
        }
    ],
    "dbPreValidations": [
        "UserIngredientsValidations"
    ]
}
```

### frontend/users_api_keys.json

User's API keys

```json
{
    "baseUrl": "users_api_keys",
    "title": "User API Keys",
    "name": "User's API Key",
    "dbApiUrl": "users_api_keys",
    "component": "UsersApiKey",
    "type": "child_listing",
    "subType": "table",
    "endpointKeyNames": [
        {
            "parameterName": "user_id",
            "parentElementName": "id"
        }
    ],
    "primaryKeyName": "id",
    "defaultOrder": "access_token",
    "fieldElements": [
        {
            "name": "id",
            "required": true,
            "label": "ID",
            "type": "_id",
            "readonly": true
        },
        {
            "name": "access_token",
            "required": true,
            "label": "Access Token",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "active",
            "required": true,
            "label": "Active",
            "type": "select",
            "select_elements": "TRUE_FALSE",
            "default_value": "1",
            "readonly": false,
            "listing": true
        }
    ],
    "dbPreRead": [
        "UsersApiKeyDbPreRead"
    ]
}
```

### frontend/users_config.json

User's configuration parameters

```json
{
  "baseUrl": "users_config",
  "title": "User Configurations",
  "name": "User's Configuration",
  "dbApiUrl": "users_config",
  "component": "UsersConfig",
  "type": "child_listing",
  "subType": "array",
  "array_name": "users_config",
  "parentUrl": "users",
  "endpointKeyNames": [
    {
      "parameterName": "user_id",
      "parentElementName": "id"
    }
  ],
  "primaryKeyName": "id",
  "defaultOrder": "config_name",
  "fieldElements": [
    {
      "name": "id",
      "required": false,
      "label": "ID",
      "type": "text",
      "readonly": true,
      "hidden": true,
      "listing": false,
      "uuid_generator": true
    },
    {
      "name": "config_name",
      "required": true,
      "label": "Name",
      "type": "text",
      "readonly": false,
      "listing": true
    },
    {
        "name": "config_value",
        "required": true,
        "label": "Value",
        "type": "text",
        "readonly": false,
        "listing": true
    }
  ]
}
```

### frontend/users_food_times.json

User's typical meal ingestion times

```json
{
  "baseUrl": "food_times",
  "title": "Food Times",
  "name": "Food Time",
  "dbApiUrl": "users_food_times",
  "component": "UsersFoodTimes",
  "type": "child_listing",
  "subType": "array",
  "array_name": "food_times",
  "parentUrl": "users",
  "endpointKeyNames": [
    {
      "parameterName": "user_id",
      "parentElementName": "id"
    }
  ],
  "primaryKeyName": "food_moment_id",
  "fieldElements": [
    {
      "name": "meal_type",
      "label": "Type",
      "required": true,
      "listing": true,
      "type": "suggestion_dropdown",
      "suggestion_id_fieldname": "_id",
      "suggestion_desc_fieldname": "name",
      "filter_api_url": "food_moments",
      "filter_api_request_method": "GET",
      "filter_search_param_name": "name",
      "filter_search_other_param": {
          "like": "1"
      }
    },
    {
      "name": "meal_time",
      "required": true,
      "label": "Time",
      "type": "text",
      "readonly": false,
      "listing": true
    }
  ]
}
```

### frontend/users_profile.json

User's profile page

```json
{
    "baseUrl": "users",
    "title": "User Profiles",
    "name": "User Profile",
    "component": "Users",
    "dbApiUrl": "users",
    "updateItem": "1",
    "fieldElements": [
        {
            "name": "id",
            "required": true,
            "label": "ID",
            "type": "_id",
            "hidden": true,
            "readonly": true
        },
        {
            "name": "firstname",
            "required": true,
            "label": "First Name",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "lastname",
            "required": true,
            "label": "Last Name",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "email",
            "required": true,
            "label": "Email",
            "type": "email",
            "readonly": false,
            "listing": true
        },
        {
            "name": "birthday",
            "required": true,
            "label": "Birthday",
            "type": "date",
            "readonly": false
        },
        {
            "name": "gender",
            "required": true,
            "label": "Gender",
            "type": "select",
            "select_elements": "GENDERS",
            "readonly": false,
            "listing": false
        },
        {
            "name": "training_days",
            "required": true,
            "label": "Training Days",
            "type": "text",
            "readonly": false
        },
        {
            "name": "training_hour",
            "required": true,
            "label": "Training Hour",
            "type": "text",
            "readonly": false
        },
        {
            "name": "height",
            "required": true,
            "label": "Height",
            "type": "number",
            "readonly": false,
            "listing": false
        },
        {
            "name": "height_unit",
            "required": true,
            "label": "Height Unit",
            "type": "select",
            "select_elements": "HEIGHT_UNITS",
            "readonly": false,
            "listing": false
        },
        {
            "name": "weight",
            "required": true,
            "label": "Weight",
            "type": "number",
            "readonly": false
        },
        {
            "name": "weight_unit",
            "required": true,
            "label": "Weight Unit",
            "type": "select",
            "select_elements": "WEIGHT_UNITS",
            "readonly": false
        },
        {
            "name": "minimun_daily_calories",
            "label": "Daily Calorie Goal",
            "type": "component",
            "component": "UserMinimumDailyCalories",
            "readonly": true,
            "listing": false
        },
        {
            "name": "goal_code",
            "required": true,
            "label": "Goal",
            "type": "select",
            "select_elements": "GOAL_CODES",
            "readonly": false,
            "listing": false
        }, 
        {
            "name": "goals",
            "required": true,
            "label": "Goal Observation",
            "type": "textarea",
            "readonly": false,
            "listing": false
        }, 
        {
            "name": "language",
            "required": true,
            "label": "Preferred Language",
            "type": "select",
            "select_elements": "LANGUAGES",
            "readonly": false,
            "listing": false
        }, 
        {
            "name": "plan",
            "required": true,
            "label": "Billing Plan",
            "type": "select",
            "select_elements": "BILLING_PLANS",
            "default_value": "free",
            "readonly": true,
            "listing": true
        }, 
        {
            "name": "status",
            "required": true,
            "label": "Active",
            "type": "select",
            "select_elements": "TRUE_FALSE",
            "default_value": "1",
            "readonly": true
        },
        {
            "name": "openai_api_key",
            "required": false,
            "label": "OpenAI API Key",
            "type": "text"
        }, 
        {
            "name": "openai_model",
            "required": false,
            "label": "OpenAI Model (defaults to gpt-4o-mini)",
            "type": "text"
        }, 
        {
            "name": "creation_date",
            "required": true,
            "label": "Client Since",
            "type": "datetime-local",
            "readonly": true,
            "hidden": false,
            "default_value": "current_timestamp",
            "listing": true
        },
        {
            "name": "label0",
            "type": "hr"
        },
        {
            "name": "label1",
            "label": "PASWORD CHANGE",
            "type": "label"
        },
        {
            "name": "passcode",
            "required": false,
            "label": "New password",
            "type": "password",
            "force_value": ""
        },
        {
            "name": "passcode_repeat",
            "required": false,
            "label": "Repeat new password",
            "type": "password",
            "force_value": ""
        }
    ],
    "childComponents": [
        "UsersFoodTimes",
        "UsersUserHistory",
        "UsersApiKey"
    ],
    "dbListPreRead": [
        "UsersDbListPreRead"
    ],
    "dbPreWrite": [
        "UsersDbPreWrite"
    ],
    "dbPostWrite": [
        "UsersDbPostWrite"
    ],
    "dbPreValidations": [
        "UsersValidations"
    ],
    "validations": [
        "UsersPasswordValidations"
    ]
}
```

### frontend/users_user_history.json

User's data history (goals, weight, etc.)

```json
{
    "baseUrl": "user_history",
    "title": "User History",
    "name": "User History",
    "component": "UsersUserHistory",
    "dbApiUrl": "users_user_history",

    "type": "child_listing",
    "subType": "array",
    "array_name": "user_history",
    "parentUrl": "users",
    "endpointKeyNames": [
        {
            "parameterName": "user_id",
            "parentElementName": "id"
        }
    ],
    "primaryKeyName": "id",
    "defaultOrder": "date|desc",
    "fieldElements": [
        {
            "name": "id",
            "required": false,
            "label": "ID",
            "type": "text",
            "readonly": true,
            "hidden": true,
            "listing": false,
            "uuid_generator": true
        },
        {
            "name": "date",
            "label": "Date",
            "required": true,
            "type": "datetime-local",
            "listing": true
        }, 
        {
            "name": "goal_code",
            "required": true,
            "label": "Goal",
            "type": "select",
            "select_elements": "GOAL_CODES",
            "readonly": false,
            "listing": true
        }, 
        {
            "name": "goals",
            "required": true,
            "label": "Goal observation",
            "type": "textarea",
            "readonly": false,
            "listing": true
        }, 
        {
            "name": "weight",
            "required": true,
            "label": "Weight",
            "type": "number",
            "readonly": false,
            "listing": true
        },
        {
            "name": "weight_unit",
            "required": true,
            "label": "Weight Unit",
            "type": "select",
            "select_elements": "WEIGHT_UNITS",
            "readonly": false,
            "listing": true
        }
    ]
}
```

### frontend/users.json

Users

```json
{
    "baseUrl": "users",
    "title": "Users",
    "name": "User",
    "component": "Users",
    "dbApiUrl": "users",
    "fieldElements": [
        {
            "name": "id",
            "required": true,
            "label": "ID",
            "type": "_id",
            "readonly": true
        },
        {
            "name": "firstname",
            "required": true,
            "label": "First Name",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "lastname",
            "required": true,
            "label": "Last Name",
            "type": "text",
            "readonly": false,
            "listing": true
        },
        {
            "name": "email",
            "required": true,
            "label": "Email",
            "type": "email",
            "readonly": false,
            "listing": true
        },
        {
            "name": "status",
            "required": true,
            "label": "Active",
            "type": "select",
            "select_elements": "TRUE_FALSE",
            "default_value": "1",
            "listing": true
        },
        {
            "name": "plan",
            "required": true,
            "label": "Billing Plan",
            "type": "select",
            "select_elements": "BILLING_PLANS",
            "default_value": "1",
            "listing": true
        }, 
        {
            "name": "superuser",
            "required": true,
            "label": "Superuser",
            "type": "select",
            "select_elements": "TRUE_FALSE",
            "readonly": false,
            "hidden": false,
            "default_value": "0",
            "listing": true
        },
        {
            "name": "birthday",
            "required": true,
            "label": "Birthday",
            "type": "date",
            "readonly": false
        },
        {
            "name": "gender",
            "required": true,
            "label": "Gender",
            "type": "select",
            "select_elements": "GENDERS",
            "readonly": false,
            "listing": false
        },
        {
            "name": "training_days",
            "required": true,
            "label": "Training Days",
            "type": "text",
            "readonly": false
        },
        {
            "name": "training_hour",
            "required": true,
            "label": "Training Hour",
            "type": "text",
            "readonly": false
        },
        {
            "name": "height",
            "required": true,
            "label": "Height",
            "type": "number",
            "readonly": false,
            "listing": false
        },
        {
            "name": "height_unit",
            "required": true,
            "label": "Height Unit",
            "type": "select",
            "select_elements": "HEIGHT_UNITS",
            "readonly": false,
            "listing": false
        },
        {
            "name": "weight",
            "required": true,
            "label": "Weight",
            "type": "number",
            "readonly": false
        },
        {
            "name": "weight_unit",
            "required": true,
            "label": "Weight Unit",
            "type": "select",
            "select_elements": "WEIGHT_UNITS",
            "readonly": false
        },
        {
            "name": "minimun_daily_calories",
            "label": "Daily Calorie Goal",
            "type": "component",
            "component": "UserMinimumDailyCalories",
            "readonly": true,
            "listing": false
        },
        {
            "name": "goal_code",
            "required": true,
            "label": "Goal",
            "type": "select",
            "select_elements": "GOAL_CODES",
            "readonly": false,
            "listing": false
        }, 
        {
            "name": "goals",
            "required": true,
            "label": "Goal Observation",
            "type": "textarea",
            "readonly": false,
            "listing": false
        }, 
        {
            "name": "language",
            "required": true,
            "label": "Preferred Language",
            "type": "select",
            "select_elements": "LANGUAGES",
            "readonly": false,
            "listing": false
        }, 
        {
            "name": "openai_api_key",
            "required": false,
            "label": "OpenAI API Key",
            "type": "text"
        }, 
        {
            "name": "openai_model",
            "required": false,
            "label": "OpenAI Model (defaults to gpt-4o-mini)",
            "type": "text"
        }, 
        {
            "name": "creation_date",
            "required": true,
            "label": "Created",
            "type": "datetime-local",
            "readonly": true,
            "hidden": false,
            "default_value": "current_timestamp",
            "listing": true
        },
        {
            "name": "update_date",
            "required": true,
            "label": "Last update",
            "type": "datetime-local",
            "readonly": true,
            "hidden": false,
            "default_value": "current_timestamp",
            "listing": false
        },
        {
            "name": "label0",
            "type": "hr"
        },
        {
            "name": "label1",
            "label": "PASWORD CHANGE",
            "type": "label"
        },
        {
            "name": "passcode",
            "required": false,
            "label": "New password",
            "type": "password",
            "force_value": ""
        },
        {
            "name": "passcode_repeat",
            "required": false,
            "label": "Repeat new password",
            "type": "password",
            "force_value": ""
        }
    ],
    "childComponents": [
        "UsersFoodTimes",
        "UsersUserHistory",
        "UsersConfig",
        "UsersApiKey"
    ],
    "dbListPreRead": [
        "UsersDbListPreRead"
    ],
    "dbPreWrite": [
        "UsersDbPreWrite"
    ],
    "dbPostWrite": [
        "UsersDbPostWrite"
    ],
    "dbPreValidations": [
        "UsersValidations"
    ],
    "validations": [
        "UsersPasswordValidations"
    ]
}
```
