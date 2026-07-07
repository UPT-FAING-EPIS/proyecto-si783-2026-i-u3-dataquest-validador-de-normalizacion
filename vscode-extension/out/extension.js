"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = require("vscode");
const cp = require("child_process");
const path = require("path");
const os = require("os");
const fs = require("fs");
function activate(context) {
    let disposable = vscode.commands.registerCommand('validador-db.analizarEsquema', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No hay un editor activo.');
            return;
        }
        const document = editor.document;
        // Si hay una selección, usarla; si no, usar todo el documento
        const selection = editor.selection;
        const text = selection.isEmpty ? document.getText() : document.getText(selection);
        if (!text.trim()) {
            vscode.window.showErrorMessage('El documento o selección está vacío.');
            return;
        }
        // Preguntar al usuario qué nivel de normalización desea
        const targetNF = await vscode.window.showQuickPick(['1FN', '2FN', '3FN'], {
            placeHolder: '¿Hasta qué Forma Normal deseas corregir automáticamente el esquema?',
            title: 'Auto-Corrección de Esquema'
        });
        if (!targetNF) {
            // Usuario canceló
            return;
        }
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Aplicando correcciones hasta ${targetNF}...`,
            cancellable: false
        }, async (progress) => {
            return new Promise((resolve) => {
                // Escribir el texto a un archivo temporal para que CLI.py lo lea
                const tempFilePath = path.join(os.tmpdir(), `esquema_${Date.now()}.sql`);
                fs.writeFileSync(tempFilePath, text, 'utf-8');
                // Encontrar la ruta de core/cli.py empaquetado dentro de la extensión
                const extensionPath = context.extensionPath;
                const cliPath = path.join(extensionPath, 'core', 'cli.py');
                if (!fs.existsSync(cliPath)) {
                    vscode.window.showErrorMessage(`No se encontró el CLI en: ${cliPath}`);
                    resolve();
                    return;
                }
                const command = `python "${cliPath}" "${tempFilePath}" --target-nf ${targetNF}`;
                cp.exec(command, (error, stdout, stderr) => {
                    // Limpiar el archivo temporal
                    if (fs.existsSync(tempFilePath)) {
                        fs.unlinkSync(tempFilePath);
                    }
                    if (error) {
                        vscode.window.showErrorMessage(`Error ejecutando análisis: ${error.message}`);
                        console.error(stderr);
                        resolve();
                        return;
                    }
                    try {
                        const reporte = JSON.parse(stdout);
                        if (reporte.error) {
                            vscode.window.showErrorMessage(`Error en análisis: ${reporte.error}`);
                            resolve();
                            return;
                        }
                        // Formatear el reporte de cambios
                        let reporteTexto = `\n\n/*\n=== REPORTE TÉCNICO DE REFACTORIZACIÓN ===\n`;
                        reporteTexto += `Objetivo: ${targetNF}\n`;
                        if (reporte.correcciones_aplicadas && reporte.correcciones_aplicadas.length > 0) {
                            reporteTexto += `\nCambios realizados:\n`;
                            reporte.correcciones_aplicadas.forEach((c) => {
                                reporteTexto += `- ${c}\n`;
                            });
                        }
                        else {
                            reporteTexto += `\nNo se detectaron violaciones o el esquema ya cumplía con ${targetNF}.\n`;
                        }
                        // Violaciones restantes que no fueron corregidas
                        let violacionesRestantes = 0;
                        if (targetNF === '1FN' || targetNF === '2FN') {
                            if (reporte.violaciones_3fn && reporte.violaciones_3fn.length > 0) {
                                violacionesRestantes += reporte.violaciones_3fn.length;
                            }
                        }
                        if (targetNF === '1FN') {
                            if (reporte.violaciones_2fn && reporte.violaciones_2fn.length > 0) {
                                violacionesRestantes += reporte.violaciones_2fn.length;
                            }
                        }
                        if (violacionesRestantes > 0) {
                            reporteTexto += `\nNOTA: Existen ${violacionesRestantes} violaciones de niveles superiores que no fueron corregidas porque no seleccionaste ese nivel.\n`;
                        }
                        reporteTexto += `==========================================\n*/\n`;
                        const sqlCorregido = reporte.sql_corregido || text;
                        const nuevoContenido = sqlCorregido + reporteTexto;
                        // Reemplazar todo el texto del documento (o de la selección)
                        editor.edit(editBuilder => {
                            if (selection.isEmpty) {
                                // Reemplazar todo el archivo
                                const fullRange = new vscode.Range(document.positionAt(0), document.positionAt(document.getText().length));
                                editBuilder.replace(fullRange, nuevoContenido);
                            }
                            else {
                                // Reemplazar solo la selección
                                editBuilder.replace(selection, nuevoContenido);
                            }
                        }).then(success => {
                            if (success) {
                                vscode.window.showInformationMessage(`¡Esquema refactorizado a ${targetNF}!`);
                            }
                            else {
                                vscode.window.showErrorMessage('No se pudo modificar el documento.');
                            }
                        });
                    }
                    catch (parseError) {
                        vscode.window.showErrorMessage('El CLI no devolvió un JSON válido.');
                        console.error("Salida original del CLI:", stdout);
                    }
                    resolve();
                });
            });
        });
    });
    context.subscriptions.push(disposable);
}
function deactivate() { }
//# sourceMappingURL=extension.js.map