import os
import re
import glob

html_dir = r"c:\Users\Dev Jayswal\Desktop\Final_application\frontend_ui_reference\stitch_cryox_antarctic_decision_support"
out_dir = r"c:\Users\Dev Jayswal\Desktop\Final_application\POLAR_NEXUS\polar_nexus\frontend\src\pages"

def camel_case_attr(match):
    prefix = match.group(1).lower()
    if prefix.startswith('data') or prefix.startswith('aria'):
        return match.group(0)
    return match.group(1) + match.group(2).upper() + match.group(3) + "="

def html_to_jsx(html):
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
    if body_match:
        content = body_match.group(1)
    else:
        content = html
    
    content = re.sub(r'<script.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<style.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)

    content = content.replace('class=', 'className=')
    content = content.replace('for=', 'htmlFor=')
    
    # Strip event handlers completely to avoid string vs function TS errors
    content = re.sub(r'\bon(click|submit|input|change)="[^"]*"', '', content, flags=re.IGNORECASE)
    
    content = content.replace('fegaussianblur', 'feGaussianBlur')
    
    for tag in ['img', 'input', 'br', 'hr']:
        content = re.sub(r'(<'+tag+r'\b[^>]*)(?<!/)>', r'\1 />', content, flags=re.IGNORECASE)
        
    svg_self_closing = ['path', 'polygon', 'circle', 'ellipse', 'line', 'rect']
    for tag in svg_self_closing:
        content = re.sub(rf'(<{tag}\b[^>]*)(?<!/)>', r'\1 />', content, flags=re.IGNORECASE)
        content = re.sub(rf'</{tag}>', '', content, flags=re.IGNORECASE)

    svg_attrs = ['stroke-width', 'stroke-dasharray', 'stroke-linecap', 'preserveaspectratio', 'viewbox', 'patternunits', 'stddeviation', 'fill-opacity', 'stroke-opacity']
    for attr in svg_attrs:
        content = re.sub(rf'\b{attr}=', lambda m: m.group(0).replace('-', '').replace('viewbox', 'viewBox').replace('preserveaspectratio', 'preserveAspectRatio').replace('patternunits', 'patternUnits').replace('stddeviation', 'stdDeviation').replace('strokewidth', 'strokeWidth').replace('strokedasharray', 'strokeDasharray').replace('strokelinecap', 'strokeLinecap').replace('fillopacity', 'fillOpacity').replace('strokeopacity', 'strokeOpacity'), content, flags=re.IGNORECASE)
        
    content = re.sub(r'\b([a-z]+)-([a-z])(\w*)=', camel_case_attr, content)
    
    content = re.sub(r'style="([^"]*)"', r'style={{ /* \1 */ }}', content)
    content = content.replace('<!--', '{/*').replace('-->', '*/}')
    content = content.replace('/> />', '/>').replace('//>', '/>')
    
    return content

directories = glob.glob(os.path.join(html_dir, '*'))

for d in directories:
    if os.path.isdir(d):
        html_file = os.path.join(d, 'code.html')
        if os.path.exists(html_file):
            name = os.path.basename(d)
            component_name = ''.join(word.title() for word in name.split('_'))
            with open(html_file, 'r', encoding='utf-8') as f:
                html = f.read()
            jsx = html_to_jsx(html)
            tsx_content = f"import React from 'react';\nimport {{ MapComponent }} from '../components/MapComponent';\n\nexport default function {component_name}() {{\n  return (\n    <>\n      {jsx}\n    </>\n  );\n}}\n"
            with open(os.path.join(out_dir, f"{component_name}.tsx"), 'w', encoding='utf-8') as f:
                f.write(tsx_content)
