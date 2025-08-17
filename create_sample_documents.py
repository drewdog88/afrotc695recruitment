#!/usr/bin/env python3
"""
Create sample PDF files for missing documents
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def create_sample_pdf(filename, title, content):
    """Create a sample PDF file"""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Add title
    title_style = styles['Heading1']
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 12))

    # Add content
    normal_style = styles['Normal']
    for paragraph in content:
        story.append(Paragraph(paragraph, normal_style))
        story.append(Spacer(1, 6))

    doc.build(story)
    print(f"✓ Created {filename}")

def main():
    """Create sample documents"""
    print("=== Creating Sample Documents ===")

    # Create documents directory if it doesn't exist
    documents_dir = "documents"
    if not os.path.exists(documents_dir):
        os.makedirs(documents_dir)

    # Define sample documents
    sample_docs = [
        {
            'filename': 'afrotc_physical_fitness_form.pdf',
            'title': 'AFROTC Physical Fitness Assessment Form',
            'content': [
                'This form is used to assess the physical fitness of AFROTC cadets.',
                'The assessment includes:',
                '• Push-ups (maximum in 1 minute)',
                '• Sit-ups (maximum in 1 minute)',
                '• 1.5 mile run (timed)',
                '• Body composition measurement',
                '',
                'Cadets must meet minimum standards to remain in the program.',
                'This form should be completed by a certified fitness instructor.',
                'Results are confidential and used for program evaluation only.'
            ]
        },
        {
            'filename': 'afrotc_scholarship_application.pdf',
            'title': 'AFROTC Scholarship Application Form',
            'content': [
                'This application is for AFROTC scholarships and financial aid.',
                'Eligibility requirements:',
                '• U.S. citizenship',
                '• High school graduate or equivalent',
                '• Minimum GPA of 3.0',
                '• Physical fitness standards',
                '• Leadership potential',
                '',
                'Scholarship benefits include:',
                '• Full tuition coverage',
                '• Monthly stipend',
                '• Book allowance',
                '• Summer training opportunities',
                '',
                'Complete all sections accurately and submit by the deadline.'
            ]
        },
        {
            'filename': 'afrotc_program_overview.pdf',
            'title': 'AFROTC Program Overview',
            'content': [
                'The Air Force Reserve Officer Training Corps (AFROTC) program',
                'provides leadership training and education for future Air Force officers.',
                '',
                'Program Components:',
                '• Academic coursework in aerospace studies',
                '• Leadership laboratory training',
                '• Physical fitness requirements',
                '• Summer field training',
                '• Professional development activities',
                '',
                'Benefits of AFROTC:',
                '• Commission as a Second Lieutenant upon graduation',
                '• Leadership and management skills',
                '• Professional development opportunities',
                '• Networking with military professionals',
                '• Potential for advanced education and training',
                '',
                'This program prepares cadets for successful careers in the U.S. Air Force.'
            ]
        },
        {
            'filename': 'cadet_handbook.pdf',
            'title': 'AFROTC Cadet Handbook',
            'content': [
                'This handbook contains the rules, regulations, and procedures',
                'for AFROTC cadets at Detachment 695.',
                '',
                'Table of Contents:',
                '1. Cadet Responsibilities',
                '2. Uniform Standards',
                '3. Academic Requirements',
                '4. Physical Fitness Standards',
                '5. Leadership Development',
                '6. Professional Conduct',
                '7. Grievance Procedures',
                '8. Emergency Contacts',
                '',
                'All cadets are responsible for knowing and following',
                'the policies outlined in this handbook.',
                'Failure to comply may result in disciplinary action.',
                '',
                'This handbook is updated annually and supersedes all previous versions.'
            ]
        },
        {
            'filename': 'leadership_development_guide.pdf',
            'title': 'Leadership Development Guide',
            'content': [
                'This guide provides a framework for developing leadership skills',
                'through AFROTC training and activities.',
                '',
                'Leadership Competencies:',
                '• Communication skills',
                '• Decision making',
                '• Team building',
                '• Problem solving',
                '• Time management',
                '• Conflict resolution',
                '• Strategic thinking',
                '',
                'Development Activities:',
                '• Leadership laboratory exercises',
                '• Community service projects',
                '• Team sports and competitions',
                '• Public speaking opportunities',
                '• Mentoring relationships',
                '',
                'Success in leadership requires continuous learning and practice.',
                'Use this guide to track your progress and set development goals.'
            ]
        }
    ]

    # Create each sample document
    for doc in sample_docs:
        file_path = os.path.join(documents_dir, doc['filename'])
        create_sample_pdf(file_path, doc['title'], doc['content'])

    print(f"\n✅ Created {len(sample_docs)} sample documents")
    print("These documents are now ready to be uploaded to Vercel Blob storage.")

if __name__ == "__main__":
    main()
