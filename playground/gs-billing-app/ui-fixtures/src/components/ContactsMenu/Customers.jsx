import React from 'react';

import * as gs from "genericsuite";
import customersConfig from "../../configs/frontend/customers.json";

const GenericCrudEditor = gs.genericEditorRfcService.GenericCrudEditor;
const GetFormData = gs.genericEditorRfcService.GetFormData;

const console_debug_log = gs.loggingService.console_debug_log;

export function Customers_EditorData() {
    console_debug_log("Customers_EditorData");
    const registry = {
        "Customers": Customers,
    }
    return GetFormData(customersConfig, registry, 'Customers_EditorData');
}

export const Customers = () => (
    <GenericCrudEditor editorConfig={Customers_EditorData()} />
)
