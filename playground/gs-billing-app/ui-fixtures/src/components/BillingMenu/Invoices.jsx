import React from 'react';

import * as gs from "genericsuite";
import invoicesConfig from "../../configs/frontend/invoices.json";

import {
    InvoiceLines,
} from './InvoiceLines.jsx';

const GenericCrudEditor = gs.genericEditorRfcService.GenericCrudEditor;
const GetFormData = gs.genericEditorRfcService.GetFormData;

const console_debug_log = gs.loggingService.console_debug_log;

export function Invoices_EditorData() {
    console_debug_log("Invoices_EditorData");
    const registry = {
        "Invoices": Invoices,
        "InvoiceLines": InvoiceLines,
    }
    return GetFormData(invoicesConfig, registry, 'Invoices_EditorData');
}

export const Invoices = () => (
    <GenericCrudEditor editorConfig={Invoices_EditorData()} />
)
