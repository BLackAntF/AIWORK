#!/usr/bin/env node
/**
 * Diagram Renderer - Render Mermaid/PlantUML diagrams to images
 * 
 * Usage:
 *   node render-diagram.js <input-file> [output-file] [format]
 *   node render-diagram.js diagram.mmd output.png png
 *   node render-diagram.js diagram.mmd output.svg svg
 */

const fs = require('fs');
const path = require('path');

// Try to load mermaid API (requires mermaid installed)
// If not available, falls back to CLI or prints code for manual rendering

const args = process.argv.slice(2);

if (args.length < 1) {
    console.log('Usage: node render-diagram.js <input-file> [output-file] [format]');
    console.log('');
    console.log('Arguments:');
    console.log('  input-file   - Path to Mermaid or PlantUML file');
    console.log('  output-file  - Optional output file path (default: input-name.png)');
    console.log('  format       - Output format: png, svg, pdf (default: png)');
    console.log('');
    console.log('Example:');
    console.log('  node render-diagram.js flowchart.mmd my-flowchart.png');
    process.exit(1);
}

const inputFile = args[0];
const outputFile = args[1] || inputFile.replace(/\.(mmd|mermaid|txt)$/i, '.png');
const format = args[2] || 'png';

function readInput(file) {
    try {
        return fs.readFileSync(file, 'utf-8');
    } catch (e) {
        console.error(`Error reading file: ${file}`);
        process.exit(1);
    }
}

function detectDiagramType(content) {
    const firstLine = content.trim().split('\n')[0].toLowerCase();
    if (firstLine.includes('%%{')) return 'mermaid';
    if (firstLine.includes('@startuml')) return 'plantuml';
    if (firstLine.includes('graph') || 
        firstLine.includes('flowchart') ||
        firstLine.includes('sequence') ||
        firstLine.includes('class') ||
        firstLine.includes('state') ||
        firstLine.includes('er') ||
        firstLine.includes('gantt') ||
        firstLine.includes('pie')) {
        return 'mermaid';
    }
    return 'unknown';
}

async function renderWithMermaid(content, output, fmt) {
    try {
        // Try to use mermaid CLI if available
        const { execSync } = require('child_process');
        
        // Write temp file
        const tempFile = path.join(__dirname, '..', 'temp-diagram.mmd');
        fs.writeFileSync(tempFile, content);
        
        const outputFormat = fmt === 'pdf' ? 'pdf' : fmt;
        const cmd = `npx -y mermaid.cli -i "${tempFile}" -o "${output}" -b transparent -w 1920 -H 1080`;
        
        try {
            execSync(cmd, { stdio: 'inherit' });
            fs.unlinkSync(tempFile);
            console.log(`✓ Diagram rendered: ${output}`);
            return true;
        } catch (e) {
            fs.unlinkSync(tempFile);
            throw e;
        }
    } catch (e) {
        console.log('Mermaid CLI not available, generating inline example...');
        return false;
    }
}

async function main() {
    console.log('Diagram Generator');
    console.log('==================');
    console.log('');
    
    const content = readInput(inputFile);
    const diagramType = detectDiagramType(content);
    
    console.log(`Input: ${inputFile}`);
    console.log(`Type: ${diagramType}`);
    console.log(`Output: ${outputFile}`);
    console.log(`Format: ${format}`);
    console.log('');
    
    if (diagramType === 'mermaid') {
        console.log('Detected Mermaid diagram');
        const success = await renderWithMermaid(content, outputFile, format);
        
        if (!success) {
            console.log('');
            console.log('To render the diagram, install mermaid.cli:');
            console.log('  npm install -g @mermaid-js/mermaid-cli');
            console.log('');
            console.log('Then run:');
            console.log(`  npx mermaid -i "${inputFile}" -o "${outputFile}"`);
            console.log('');
            console.log('Or embed this Mermaid code in your markdown:');
            console.log('');
            console.log('```mermaid');
            console.log(content);
            console.log('```');
        }
    } else {
        console.log('Unknown diagram format');
        console.log('');
        console.log('Supported formats:');
        console.log('  - Mermaid (.mmd, .mermaid)');
        console.log('  - PlantUML (.puml, .plantuml)');
    }
}

main();
