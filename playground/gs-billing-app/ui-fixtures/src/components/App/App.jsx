import React from 'react';

import { App as GsApp } from "genericsuite";

import { Invoices } from '../BillingMenu/Invoices.jsx';
import { Customers } from '../ContactsMenu/Customers.jsx';
import { HomePage } from '../HomePage/HomePage.jsx';

const AppLogo = 'app_logo_circle.svg';
const AppLogoHeader = 'app_logo_horizontal.svg';

const componentMap = {
    "Invoices": Invoices,
    "Customers": Customers,
    "HomePage": HomePage,
};

export const App = () => {
    return (
        <GsApp
            appLogo={AppLogo}
            appLogoHeader={AppLogoHeader}
            componentMap={componentMap}
        />
    );
}
