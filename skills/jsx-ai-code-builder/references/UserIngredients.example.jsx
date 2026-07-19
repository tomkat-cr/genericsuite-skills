import React from 'react';

import * as gs from "genericsuite";
import * as gsAi from "genericsuite-ai";

import user_ingredients from "../../configs/frontend/user_ingredients.json";
import {
    CALORIE_UNITS,
    INGREDIENT_TYPE,
    SERVING_SIZE_UNITS,
} from '../../constants/app_constants.jsx';

const useUser = gs.UserContext.useUser;
const GenericCrudEditor = gs.genericEditorRfcService.GenericCrudEditor;
const GetFormData = gs.genericEditorRfcService.GetFormData;
const GenericSelectGenerator = gs.genericEditorRfcSelector.GenericSelectGenerator;
const GenericSelectDataPopulator = gs.genericEditorRfcSelector.GenericSelectDataPopulator;
const genericFuncArrayDefaultValue = gs.genericEditorRfcSpecificFunc.genericFuncArrayDefaultValue;
const console_debug_log = gs.loggingService.console_debug_log;
const ChatBotButton = gsAi.ChatBotButton;


export function UserIngredients_EditorData() {
    // console_debug_log("UserIngredients_EditorData");
    const registry = {
        "UserIngredients": UserIngredients,
        "UserIngredientsDataPopulator": UserIngredientsDataPopulator,
        "UserIngredientsValidations": UserIngredientsValidations,
        "CALORIE_UNITS": CALORIE_UNITS,
        "SERVING_SIZE_UNITS": SERVING_SIZE_UNITS,
        "INGREDIENT_TYPE": INGREDIENT_TYPE,
        "ChatBotButton": ChatBotButton,
    }
    return GetFormData(user_ingredients, registry, 'UserIngredients_EditorData');
}

export const UserIngredients = () => (
    <GenericCrudEditor editorConfig={UserIngredients_EditorData()} />
)

export const UserIngredientsSelect = (props) => {
    // const { currentUserValue } = authenticationService;
    // const user_id_filter = {'user_id': currentUserValue.id}
    const { currentUser } = useUser();
    const user_id_filter = { 'user_id': currentUser.id }
    console_debug_log("*** UserIngredientsSelect *** | user_id_filter:");
    console_debug_log(user_id_filter);
    return (
        <GenericSelectGenerator
            filter={typeof props.filter == 'undefined' ? null : props.filter}
            show_description={typeof props.show_description == 'undefined' ? false : props.show_description}
            editorConfig={UserIngredients_EditorData()}
            dbFilter={user_id_filter}
        />
    )
}

export const UserIngredientsDataPopulator = () => {
    const { currentUser } = useUser();
    const user_id_filter = { 'user_id': currentUser.id }
    console_debug_log("*** UserIngredientsDataPopulator *** | user_id_filter:");
    console_debug_log(user_id_filter);
    return (
        <GenericSelectDataPopulator
            editorConfig={UserIngredients_EditorData()}
            dbFilter={user_id_filter}
        />
    );
}

export const UserIngredientsValidations = (data, editor, action) => {
    // user_ingredients / dishes pre-deletion validations
    return new Promise((resolve, reject) => {
        let resp = genericFuncArrayDefaultValue(data);
        switch (action) {
            // //
            // // Example of pre-deletion validations to avoid deleting a user_ingredient
            // // that is referenced in user_ingredients_in_user
            // //
            // case ACTION_DELETE:
            //     const db = new dbApiService({ url: `${editor.dbApiUrl}/user_ingredients_in_user` });
            //     const users_ingredient_id = convertId(data['_id'])
            //     db.getOne({id: users_ingredient_id}).then( 
            //         data => {
            //             if (data['resultset']['rows_count'] > 0) {
            //                 resp.error = true;
            //                 resp.errorMsg = (resp.errorMsg === '' ? '' : '<br>') + 
            //                     'Cannot delete because it\'s referenced ' + 
            //                     data['resultset']['rows_count'] + ' times in ' +
            //                     ' in User\'s Daily Meals.';
            //             }
            //             if (resp.error) {
            //                 reject(resp);
            //             } else {
            //                 resolve(resp);
            //             }
            //         },
            //         error => {
            //             resp.error = true;
            //             resp.errorMsg = error;
            //             reject(resp)
            //         }
            //     );
            //     break;
            default:
                resolve(resp);
        }
    });
}
