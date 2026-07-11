import React from 'react';

// import * as gs from "genericsuite";
import { App as GsAiApp } from "genericsuite-ai";

import { FoodMoments_EditorData } from '../SuperAdminOptions/FoodMoments.jsx';
import { GeneralIngredients_EditorData } from '../SuperAdminOptions/GeneralIngredients.jsx';
import { UserIngredients_EditorData } from '../UsersMenu/UserIngredients.jsx';
import { Dishes_EditorData } from '../UsersMenu/Dishes.jsx';
import { DailyMeals_EditorData } from '../UsersMenu/DailyMeals.jsx';
import { UserProfileEditor } from '../UsersMenu/UserProfile.jsx';
import { ClarifaiModels_EditorData } from '../SuperAdminOptions/ClarifaiModels.jsx';
import { Users_EditorData } from '../SuperAdminOptions/Users.jsx';

import { HomePage } from '../HomePage/HomePage.jsx';
import { AboutBody } from '../About/About.jsx';

// const AppLogo = 'app_logo_square.svg';
const AppLogo = 'app_logo_circle.svg';
const AppLogoHeader = 'app_logo_horizontal.svg';

const componentMap = {
    "FoodMoments_EditorData": FoodMoments_EditorData,
    "GeneralIngredients_EditorData": GeneralIngredients_EditorData,
    "ClarifaiModels_EditorData": ClarifaiModels_EditorData,
    "UserIngredients_EditorData": UserIngredients_EditorData,
    "Dishes_EditorData": Dishes_EditorData,
    "DailyMeals_EditorData": DailyMeals_EditorData,
    "UserProfileEditor": UserProfileEditor,
    "Users_EditorData": Users_EditorData,
    "AboutBody": AboutBody,
    "HomePage": HomePage,
};

export const App = () => {
    return (
        <GsAiApp
            appLogo={AppLogo}
            appLogoHeader={AppLogoHeader}
            componentMap={componentMap}
        />
    );
}