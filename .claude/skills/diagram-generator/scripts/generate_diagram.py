#!/usr/bin/env python3
"""
Diagram Generator - Generate Visio-style diagrams using Python

This module provides functions to create professional diagrams using matplotlib.
It supports flowcharts, architecture diagrams, class diagrams, and more.

Requirements:
    pip install matplotlib numpy

Usage:
    python generate_diagram.py <diagram-type> <output-file>
    
    Diagram types:
        - flowchart: Simple process flow
        - architecture: System architecture
        - layers: Layered architecture
        - sequence: Sequence diagram
"""

import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import numpy as np

def create_flowchart(nodes, edges, output_file='flowchart.png'):
    """
    Create a flowchart diagram.
    
    Args:
        nodes: List of (id, label, shape) tuples
        edges: List of (from_id, to_id, label) tuples
        output_file: Output file path
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(-1, 13)
    ax.set_ylim(-1, 9)
    ax.axis('off')
    
    # Node positions (simple grid layout)
    pos = {}
    rows = 3
    cols = 4
    for i, (node_id, label, shape) in enumerate(nodes):
        row = i // cols
        col = i % cols
        x = col * 3 + 1.5
        y = 7 - row * 2.5
        pos[node_id] = (x, y)
        
        # Draw node based on shape
        if shape == 'terminal':
            bbox = FancyBboxPatch((x - 0.8, y - 0.3), 1.6, 0.6,
                                  boxstyle="round,pad=0.05,rounding_size=0.3",
                                  facecolor='#4CAF50', edgecolor='#388E3C', linewidth=2)
        elif shape == 'decision':
            bbox = FancyBboxPatch((x - 0.6, y - 0.4), 1.2, 0.8,
                                  boxstyle="round,pad=0.05,rounding_size=0.1",
                                  facecolor='#FFC107', edgecolor='#FFA000', linewidth=2,
                                  mutation_scale=1.2)
            # Diamond shape approximation
            diamond = plt.Polygon([(x, y + 0.5), (x + 0.6, y), (x, y - 0.5), (x - 0.6, y)],
                                 facecolor='#FFC107', edgecolor='#FFA000', linewidth=2)
            ax.add_patch(diamond)
            ax.text(x, y, label, ha='center', va='center', fontsize=9, fontweight='bold')
            if node_id in pos:
                pos[node_id] = (x, y)
            continue
        else:  # process
            bbox = FancyBboxPatch((x - 0.8, y - 0.3), 1.6, 0.6,
                                  boxstyle="round,pad=0.05,rounding_size=0.1",
                                  facecolor='#2196F3', edgecolor='#1976D2', linewidth=2)
        ax.add_patch(bbox)
        ax.text(x, y, label, ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Draw edges
    for (from_id, to_id, label) in edges:
        if from_id in pos and to_id in pos:
            x1, y1 = pos[from_id]
            x2, y2 = pos[to_id]
            
            # Draw arrow
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1 - 0.3),
                       arrowprops=dict(arrowstyle='->', color='#666666', lw=1.5))
            
            # Label
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2 - 0.5
            ax.text(mid_x, mid_y, label, ha='center', va='center', fontsize=8, 
                   bbox=dict(boxstyle='round', facecolor='white', edgecolor='none', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Flowchart saved to: {output_file}')


def create_architecture(layers, output_file='architecture.png'):
    """
    Create a layered architecture diagram.
    
    Args:
        layers: List of (layer_name, components) tuples
                components: List of component names
        output_file: Output file path
    """
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(-2, 16)
    ax.set_ylim(-1, 12)
    ax.axis('off')
    
    colors = ['#E3F2FD', '#BBDEFB', '#90CAF9', '#64B5F6', '#42A5F5', '#2196F3']
    
    y_pos = 11
    for i, (layer_name, components) in enumerate(layers):
        # Draw layer box
        layer_height = max(1.5, len(components) * 0.5 + 0.5)
        bbox = FancyBboxPatch((0.5, y_pos - layer_height), 14, layer_height,
                              boxstyle="round,pad=0.1,rounding_size=0.2",
                              facecolor=colors[i % len(colors)],
                              edgecolor='#1976D2', linewidth=2)
        ax.add_patch(bbox)
        
        # Layer label
        ax.text(7.5, y_pos - 0.3, layer_name, ha='center', va='top', 
               fontsize=12, fontweight='bold', color='#1565C0')
        
        # Components
        comp_width = 13 / max(len(components), 1)
        for j, comp in enumerate(components):
            x = 1 + j * comp_width + comp_width / 2
            y = y_pos - layer_height / 2 - 0.3
            
            # Component box
            comp_box = FancyBboxPatch((x - comp_width/2 + 0.2, y - 0.25), 
                                      comp_width - 0.4, 0.5,
                                      boxstyle="round,pad=0.05,rounding_size=0.1",
                                      facecolor='white', edgecolor='#42A5F5', linewidth=1.5)
            ax.add_patch(comp_box)
            ax.text(x, y, comp, ha='center', va='center', fontsize=9)
        
        y_pos -= layer_height + 0.5
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Architecture diagram saved to: {output_file}')


def create_class_diagram(classes, relationships, output_file='class_diagram.png'):
    """
    Create a UML class diagram.
    
    Args:
        classes: List of (class_name, attributes, methods) tuples
        relationships: List of (from_class, to_class, type) tuples
    """
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(-2, 18)
    ax.set_ylim(-1, 14)
    ax.axis('off')
    
    # Position classes
    pos = {}
    cols = 3
    for i, (class_name, attrs, methods) in enumerate(classes):
        col = i % cols
        row = i // cols
        x = 2 + col * 5.5
        y = 11 - row * 4
        pos[class_name] = (x, y)
        
        # Calculate box size
        max_len = max(len(class_name), max((len(a) for a in attrs), default=0),
                     max((len(m) for m in methods), default=0))
        box_width = min(max_len * 0.15 + 0.5, 4)
        box_height = 0.4 + len(attrs) * 0.35 + len(methods) * 0.35
        
        # Draw class box
        bbox = FancyBboxPatch((x - box_width/2, y - box_height), box_width, box_height,
                              boxstyle="round,pad=0.05",
                              facecolor='white', edgecolor='black', linewidth=2)
        ax.add_patch(bbox)
        
        # Class name
        ax.text(x, y - 0.2, class_name, ha='center', va='top', 
               fontsize=10, fontweight='bold')
        ax.plot([x - box_width/2, x + box_width/2], [y - 0.4, y - 0.4], 'k-', linewidth=1)
        
        # Attributes
        for j, attr in enumerate(attrs):
            ax.text(x - box_width/2 + 0.1, y - 0.55 - j * 0.35, attr,
                   ha='left', va='top', fontsize=8)
        
        if attrs:
            ax.plot([x - box_width/2, x + box_width/2], 
                   [y - 0.55 - len(attrs) * 0.35, y - 0.55 - len(attrs) * 0.35], 'k-', linewidth=1)
        
        # Methods
        for j, method in enumerate(methods):
            ax.text(x - box_width/2 + 0.1, 
                   y - 0.7 - len(attrs) * 0.35 - j * 0.35, method,
                   ha='left', va='top', fontsize=8)
    
    # Draw relationships
    for (from_class, to_class, rel_type) in relationships:
        if from_class in pos and to_class in pos:
            x1, y1 = pos[from_class]
            x2, y2 = pos[to_class]
            
            if rel_type == 'inheritance':
                ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                           arrowprops=dict(arrowstyle='-|>', color='black', lw=1.5))
            elif rel_type == 'association':
                ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                           arrowprops=dict(arrowstyle='->', color='black', lw=1))
            elif rel_type == 'composition':
                ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                           arrowprops=dict(arrowstyle='-|>', color='black', lw=1.5,
                                         patchB=None))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Class diagram saved to: {output_file}')


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_diagram.py <diagram-type> [output-file]")
        print("")
        print("Diagram types:")
        print("  flowchart    - Simple process flow")
        print("  architecture - System architecture")
        print("  layers      - Layered architecture")
        print("  class       - UML class diagram")
        print("")
        print("Examples:")
        print("  python generate_diagram.py flowchart myflow.png")
        print("  python generate_diagram.py architecture arch.png")
        sys.exit(1)
    
    diagram_type = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f'{diagram_type}.png'
    
    if diagram_type == 'flowchart':
        # Example flowchart
        nodes = [
            ('start', '开始', 'terminal'),
            ('check', '是否登录?', 'decision'),
            ('login', '登录', 'process'),
            ('reg', '注册', 'process'),
            ('home', '首页', 'process'),
            ('end', '结束', 'terminal'),
        ]
        edges = [
            ('start', 'check', ''),
            ('check', 'login', '是'),
            ('check', 'reg', '否'),
            ('reg', 'login', ''),
            ('login', 'home', ''),
            ('home', 'end', ''),
        ]
        create_flowchart(nodes, edges, output_file)
    
    elif diagram_type == 'architecture':
        # Example architecture
        layers = [
            ('前端层', ['Web应用', '移动APP', '管理后台']),
            ('网关层', ['API网关', '认证服务']),
            ('业务层', ['用户服务', '订单服务', '支付服务']),
            ('数据层', ['MySQL', 'Redis', 'MongoDB']),
        ]
        create_architecture(layers, output_file)
    
    elif diagram_type == 'layers':
        layers = [
            ('表现层', ['Controller', 'View']),
            ('业务层', ['Service']),
            ('持久层', ['DAO', 'Repository']),
            ('数据层', ['Database']),
        ]
        create_architecture(layers, output_file)
    
    elif diagram_type == 'class':
        # Example class diagram
        classes = [
            ('User', ['-id: int', '-name: str', '-email: str'], ['+login()', '+logout()']),
            ('Order', ['-id: int', '-userId: int', '-total: float'], ['+create()', '+cancel()']),
            ('Product', ['-id: int', '-name: str', '-price: float'], ['+getPrice()']),
        ]
        relationships = [
            ('User', 'Order', 'association'),
            ('Order', 'Product', 'association'),
        ]
        create_class_diagram(classes, relationships, output_file)
    
    else:
        print(f"Unknown diagram type: {diagram_type}")
        sys.exit(1)


if __name__ == '__main__':
    main()
