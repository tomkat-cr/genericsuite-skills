import React from 'react';

import * as gs from "genericsuite";
import invoiceLinesConfig from "../../configs/frontend/invoice_lines.json";

const GenericCrudEditor = gs.genericEditorRfcService.GenericCrudEditor;
const GetFormData = gs.genericEditorRfcService.GetFormData;

export function InvoiceLines_EditorData() {
    const registry = {
        "InvoiceLines": InvoiceLines,
    }
    return GetFormData(invoiceLinesConfig, registry, false);
}

export const InvoiceLines = ({parentData, handleFormPageActions}) => (
    <GenericCrudEditor
        editorConfig={InvoiceLines_EditorData()}
        parentData={parentData}
        handleFormPageActions={handleFormPageActions}
    />
)
