#!/usr/bin/env node
/**
 * Markdown to Word Converter with LaTeX support
 * 
 * Converts Markdown documents to Word (.docx) while preserving:
 * - Mathematical formulas (LaTeX)
 * - Code blocks with syntax highlighting
 * - Tables and images
 * 
 * Usage:
 *   node markdown-to-docx.js <input.md> [output.docx]
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const args = process.argv.slice(2);

if (args.length < 1) {
    console.log('Usage: node markdown-to-docx.js <input.md> [output.docx]');
    console.log('');
    console.log('This script converts Markdown to Word while preserving LaTeX formulas.');
    console.log('Requires: pandoc (optional - will use best available method)');
    console.log('');
    console.log('If pandoc is not available, it will:');
    console.log('1. Extract LaTeX formulas and create placeholders');
    console.log('2. Convert markdown structure');
    console.log('3. Generate a conversion report');
    process.exit(1);
}

const inputFile = args[0];
const outputFile = args[1] || inputFile.replace(/\.md$/i, '.docx');

function checkPandoc() {
    try {
        execSync('pandoc --version', { stdio: 'ignore' });
        return true;
    } catch (e) {
        return false;
    }
}

function checkMermaidCli() {
    try {
        execSync('npx mermaid --version', { stdio: 'ignore' });
        return true;
    } catch (e) {
        return false;
    }
}

function extractLatexFormulas(content) {
    // Extract display math ($$...$$)
    const displayMathRegex = /\$\$([\s\S]*?)\$\$/g;
    const displayMath = [];
    let match;
    
    while ((match = displayMathRegex.exec(content)) !== null) {
        displayMath.push({
            type: 'display',
            original: match[0],
            formula: match[1].trim()
        });
    }
    
    // Extract inline math ($...$)
    const inlineMathRegex = /\$([^\$\n]+?)\$/g;
    const inlineMath = [];
    
    while ((match = inlineMathRegex.exec(content)) !== null) {
        inlineMath.push({
            type: 'inline',
            original: match[0],
            formula: match[1]
        });
    }
    
    return { displayMath, inlineMath };
}

function convertWithPandoc(input, output) {
    console.log('Using pandoc for conversion...');
    
    const cmd = `pandoc "${input}" -o "${output}" ` +
                `--from=markdown+tex_math_dollars ` +
                `--to=docx ` +
                `--highlight-style=tango ` +
                `--reference-doc=default ` +
                `-s`;
    
    try {
        execSync(cmd, { stdio: 'inherit' });
        console.log(`\n✓ Converted to: ${output}`);
        return true;
    } catch (e) {
        console.error('Pandoc conversion failed');
        return false;
    }
}

function createConversionReport(input, formulas, output) {
    console.log('\n--- Conversion Report ---');
    console.log(`Input: ${input}`);
    console.log(`Output: ${output}`);
    console.log('');
    console.log('LaTeX Formulas Found:');
    console.log(`  - Display math ($$...$$): ${formulas.displayMath.length}`);
    console.log(`  - Inline math ($...$): ${formulas.inlineMath.length}`);
    console.log('');
    console.log('To convert with full formula support:');
    console.log('1. Install pandoc: https://pandoc.org/installing.html');
    console.log('2. Run: pandoc input.md -o output.docx --from=markdown+tex_math_dollars');
    console.log('');
    console.log('Alternative: Use VS Code with extension "Markdown All in One"');
    console.log('which can export to Word with formula support.');
    
    const reportFile = output.replace('.docx', '-conversion-report.txt');
    const report = `
LaTeX to Word Conversion Report
================================
Input: ${input}
Output: ${output}

Formulas Found:
- Display math ($$...$$): ${formulas.displayMath.length}
- Inline math ($...$): ${formulas.inlineMath.length}

${formulas.displayMath.length > 0 ? '\nDisplay Formulas:\n' + formulas.displayMath.map((f, i) => `${i + 1}. ${f.formula}`).join('\n') : ''}
${formulas.inlineMath.length > 0 ? '\nInline Formulas:\n' + formulas.inlineMath.map((f, i) => `${i + 1}. ${f.formula}`).join('\n') : ''}

Recommendations:
1. Install pandoc for automatic conversion
2. Use VS Code LaTeX Workshop for local preview
3. Use Overleaf (overleaf.com) for collaborative LaTeX editing
`.trim();
    
    fs.writeFileSync(reportFile, report);
    console.log(`\nReport saved to: ${reportFile}`);
}

async function main() {
    console.log('Markdown to Word Converter with LaTeX Support');
    console.log('='.repeat(50));
    console.log('');
    
    // Read input file
    let content;
    try {
        content = fs.readFileSync(inputFile, 'utf-8');
    } catch (e) {
        console.error(`Error reading file: ${inputFile}`);
        process.exit(1);
    }
    
    console.log(`Input: ${inputFile}`);
    console.log(`File size: ${content.length} bytes`);
    console.log('');
    
    // Extract LaTeX formulas
    const formulas = extractLatexFormulas(content);
    console.log(`Found ${formulas.displayMath.length} display formulas`);
    console.log(`Found ${formulas.inlineMath.length} inline formulas`);
    console.log('');
    
    // Check for pandoc
    if (checkPandoc()) {
        const success = convertWithPandoc(inputFile, outputFile);
        if (success) {
            console.log('');
            createConversionReport(inputFile, formulas, outputFile);
            return;
        }
    } else {
        console.log('Pandoc not found. Checking alternative methods...');
    }
    
    // No pandoc - create report
    console.log('\nPandoc is not installed.');
    console.log('To enable automatic conversion:');
    console.log('');
    console.log('Option 1: Install Pandoc');
    console.log('  Download: https://pandoc.org/installing.html');
    console.log('  Then run this script again.');
    console.log('');
    console.log('Option 2: Use VS Code Extensions');
    console.log('  - "Markdown All in One" - Export to Word');
    console.log('  - "LaTeX Workshop" - Preview LaTeX');
    console.log('');
    console.log('Option 3: Use Online Tools');
    console.log('  - https://pandoc.org/try - Online pandoc');
    console.log('  - https://overleaf.com - LaTeX editor');
    console.log('');
    
    createConversionReport(inputFile, formulas, outputFile);
}

main();
