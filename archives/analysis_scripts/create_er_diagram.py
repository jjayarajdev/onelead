#!/usr/bin/env python3
"""
Create ER Diagram for HPE DataExportAug29th.xlsx relationships
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.lines as mlines

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(20, 14))
ax.set_xlim(0, 20)
ax.set_ylim(0, 14)
ax.axis('off')

# Color scheme
entity_color = '#E8F4FD'
entity_border = '#2196F3'
pk_color = '#FFE082'
fk_color = '#C5E1A5'
attr_color = '#FFFFFF'

def draw_entity(ax, x, y, width, height, name, attributes, pks=[], fks=[]):
    """Draw an entity box with attributes"""
    # Entity box
    entity_box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.02",
        facecolor=entity_color,
        edgecolor=entity_border,
        linewidth=2
    )
    ax.add_patch(entity_box)
    
    # Entity name (header)
    ax.text(x + width/2, y + height - 0.25, name, 
           fontsize=11, fontweight='bold', 
           ha='center', va='center')
    
    # Separator line
    ax.plot([x + 0.1, x + width - 0.1], 
           [y + height - 0.5, y + height - 0.5], 
           'k-', linewidth=1)
    
    # Attributes
    attr_y = y + height - 0.8
    for attr in attributes:
        # Determine if PK or FK
        if attr in pks:
            marker = '🔑 '
            bg_color = pk_color
        elif attr in fks:
            marker = '🔗 '
            bg_color = fk_color
        else:
            marker = '• '
            bg_color = attr_color
        
        # Add attribute with background
        if attr in pks or attr in fks:
            attr_box = FancyBboxPatch(
                (x + 0.1, attr_y - 0.15), width - 0.2, 0.3,
                boxstyle="round,pad=0.01",
                facecolor=bg_color,
                edgecolor='none',
                alpha=0.5
            )
            ax.add_patch(attr_box)
        
        # Use text markers instead of emojis
        if attr in pks:
            display_text = '[PK] ' + attr
        elif attr in fks:
            display_text = '[FK] ' + attr
        else:
            display_text = '  ' + attr
            
        ax.text(x + 0.15, attr_y, display_text, 
               fontsize=8, va='center')
        attr_y -= 0.35

def draw_relationship(ax, x1, y1, x2, y2, label='', rel_type='one-to-many', style='solid'):
    """Draw relationship line between entities"""
    # Determine line style
    if style == 'dashed':
        linestyle = '--'
        alpha = 0.5
    else:
        linestyle = '-'
        alpha = 1.0
    
    # Draw arrow
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        connectionstyle="arc3,rad=0.1",
        arrowstyle='->',
        linestyle=linestyle,
        linewidth=1.5,
        color='#666666',
        alpha=alpha
    )
    ax.add_patch(arrow)
    
    # Add label
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    if label:
        ax.text(mid_x, mid_y, label, 
               fontsize=8, ha='center',
               bbox=dict(boxstyle="round,pad=0.3", 
                        facecolor='white', 
                        edgecolor='gray',
                        alpha=0.8))
    
    # Add cardinality notation
    if rel_type == 'one-to-many':
        ax.text(x1 - 0.2, y1, '1', fontsize=9, fontweight='bold')
        ax.text(x2 + 0.2, y2, 'N', fontsize=9, fontweight='bold')
    elif rel_type == 'many-to-many':
        ax.text(x1 - 0.2, y1, 'N', fontsize=9, fontweight='bold')
        ax.text(x2 + 0.2, y2, 'M', fontsize=9, fontweight='bold')

# Title
ax.text(10, 13.5, 'HPE DataExportAug29th - Entity Relationship Diagram', 
       fontsize=16, fontweight='bold', ha='center')

# Define entities with their attributes
# Install Base
draw_entity(ax, 1, 8, 4, 3.5, 'INSTALL_BASE',
           ['Serial_Number_Id', 'Account_Sales_Territory_Id', 'Product_Id',
            'Product_Platform_Description', 'Product_Name', 'Product_End_of_Life_Date',
            'Support_Status', 'Service_Agreement_Id'],
           pks=['Serial_Number_Id'],
           fks=['Account_Sales_Territory_Id'])

# Opportunity
draw_entity(ax, 7, 8, 4, 2.8, 'OPPORTUNITY',
           ['HPE_Opportunity_ID', 'Account_ST_ID', 'Opportunity_Name',
            'Account_Name', 'Product_Line'],
           pks=['HPE_Opportunity_ID'],
           fks=['Account_ST_ID'])

# A&PS Projects
draw_entity(ax, 1, 3, 4, 3.8, 'APS_PROJECTS',
           ['Project', 'PRJ_Customer_ID', 'PRJ_Description',
            'PRJ_Practice', 'PRJ_Start_Date', 'PRJ_End_Date',
            'PRJ_Status_Description', 'Country', 'PRJ_Size'],
           pks=['Project'],
           fks=['PRJ_Customer_ID'])

# Service Credits
draw_entity(ax, 7, 3, 4, 3.2, 'SERVICE_CREDITS',
           ['ProjectID', 'ProjectName', 'PracticeName',
            'PurchasedCredits', 'DeliveredCredits', 'ActiveCredits',
            'ContractEndDate', 'ExpiryInDays'],
           pks=['ProjectID'],
           fks=[])

# Services (Reference)
draw_entity(ax, 13, 5.5, 4, 2.5, 'SERVICES',
           ['Practice', 'Sub_Practice', 'Services'],
           pks=['Practice', 'Sub_Practice', 'Services'],
           fks=[])

# Customer Account (Virtual/Implied Entity)
draw_entity(ax, 13, 9, 4, 2.2, 'CUSTOMER_ACCOUNT',
           ['Account_ID_5digit', 'Account_ID_9digit',
            'Account_Name', 'Territory'],
           pks=['Account_ID_5digit'],
           fks=[])

# Draw relationships

# Install Base to Opportunity (Strong - Direct FK)
draw_relationship(ax, 5, 9.5, 7, 9.5, 
                  'shares Account_ST_ID', 'one-to-many', 'solid')

# Install Base to Customer Account
draw_relationship(ax, 5, 10, 13, 10, 
                  '', 'one-to-many', 'solid')

# Opportunity to Customer Account  
draw_relationship(ax, 11, 9.5, 13, 9.5,
                  '', 'one-to-many', 'solid')

# APS Projects to different Customer system (Weak - Different ID system)
draw_relationship(ax, 5, 5, 13, 8,
                  'Different ID System\n(9-digit vs 5-digit)', 'one-to-many', 'dashed')

# Service Credits to Projects (Weak - Different ID format)
draw_relationship(ax, 5, 4.5, 7, 4.5,
                  'Different Project ID\nFormat', 'many-to-many', 'dashed')

# Services to APS Projects (Reference relationship)
draw_relationship(ax, 13, 6, 5, 5,
                  'Practice\nTaxonomy', 'one-to-many', 'dashed')

# Services to Service Credits (Reference relationship)
draw_relationship(ax, 13, 6.5, 11, 5,
                  'Practice\nReference', 'one-to-many', 'dashed')

# Add legend
legend_x = 0.5
legend_y = 1
ax.text(legend_x, legend_y + 0.5, 'Legend:', fontsize=10, fontweight='bold')

# PK indicator
pk_box = FancyBboxPatch((legend_x, legend_y), 2, 0.3,
                        boxstyle="round,pad=0.01",
                        facecolor=pk_color, edgecolor='none', alpha=0.5)
ax.add_patch(pk_box)
ax.text(legend_x + 0.1, legend_y + 0.15, '[PK] Primary Key', fontsize=8, va='center')

# FK indicator
fk_box = FancyBboxPatch((legend_x, legend_y - 0.4), 2, 0.3,
                        boxstyle="round,pad=0.01",
                        facecolor=fk_color, edgecolor='none', alpha=0.5)
ax.add_patch(fk_box)
ax.text(legend_x + 0.1, legend_y - 0.25, '[FK] Foreign Key', fontsize=8, va='center')

# Solid line
ax.plot([legend_x + 2.5, legend_x + 3.5], [legend_y + 0.15, legend_y + 0.15],
        'k-', linewidth=1.5)
ax.text(legend_x + 3.7, legend_y + 0.15, 'Direct Relationship', fontsize=8, va='center')

# Dashed line
ax.plot([legend_x + 2.5, legend_x + 3.5], [legend_y - 0.25, legend_y - 0.25],
        'k--', linewidth=1.5, alpha=0.5)
ax.text(legend_x + 3.7, legend_y - 0.25, 'Indirect/Weak Relationship', fontsize=8, va='center')

# Add notes
notes_text = """
Key Insights:
• Install Base and Opportunity share customer IDs (5-digit format)
• A&PS Projects uses different customer ID system (9-digit format)
• Service Credits and A&PS Projects use incompatible project ID formats
• Services sheet provides reference taxonomy but with inconsistent naming
• Customer Account entity is implied but not explicitly present in data
"""

ax.text(18.5, 2, notes_text, fontsize=9, 
       verticalalignment='top',
       bbox=dict(boxstyle="round,pad=0.5", 
                facecolor='#FFFDE7', 
                edgecolor='#F57C00',
                linewidth=1))

# Add cardinality descriptions
card_text = """
Cardinality Notation:
1 : One (exactly one)
N : Many (zero or more)
"""
ax.text(18.5, 12, card_text, fontsize=9,
       bbox=dict(boxstyle="round,pad=0.3",
                facecolor='white',
                edgecolor='gray'))

plt.title('Entity Relationships in HPE Data Export', fontsize=14, pad=20)
plt.tight_layout()

# Save the diagram
output_path = '/Users/jjayaraj/workspaces/HPE/onelead_system/data/er_diagram.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', 
           facecolor='white', edgecolor='none')
print(f"ER Diagram saved to: {output_path}")

# Also save as PDF for better quality
pdf_path = '/Users/jjayaraj/workspaces/HPE/onelead_system/data/er_diagram.pdf'
plt.savefig(pdf_path, format='pdf', bbox_inches='tight',
           facecolor='white', edgecolor='none')
print(f"ER Diagram (PDF) saved to: {pdf_path}")

# plt.show()  # Commented out to prevent GUI display