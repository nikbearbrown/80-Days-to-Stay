from IPython.display import Image, display

workflow = None 
# Generate PNG
png_bytes = workflow.get_graph().draw_mermaid_png()

# Save to file
with open("workflow.png", "wb") as f:
    f.write(png_bytes)
