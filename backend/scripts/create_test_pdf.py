import fitz

def create_sample_pdf():
    doc = fitz.open()
    page = doc.new_page()
    
    text = """
    Lecture 1: Introduction to Physics
    Date: 2024-02-12
    
    Newton's Second Law:
    The force F acting on an object is equal to the mass m times its acceleration a.
    
    Formula:
    F = ma
    
    Energy-Mass Equivalence:
    E = mc^2
    """
    
    page.insert_text((50, 50), text, fontsize=12)
    doc.save("sample_notes.pdf")
    print("Created sample_notes.pdf")

if __name__ == "__main__":
    create_sample_pdf()
