# ============================================================
# services/pdf_extractor.py
# ============================================================

"""
Document Text Extractor
-----------------------

Extracts text from:

- PDF files
- DOCX files
- Images (JPG, JPEG, PNG)

Features:

- Direct text extraction from normal PDFs
- OCR fallback for scanned/image-based PDFs
- OCR extraction from certificate images
- DOCX text extraction
- Image preprocessing for better OCR accuracy

Used by:
- routes/upload_routes.py
- services/skill_extractor.py
"""


import os

import fitz

from docx import Document

from PIL import (
    Image,
    ImageOps,
    ImageEnhance,
    ImageFilter
)

import pytesseract


# ============================================================
# TESSERACT OCR CONFIGURATION
# ============================================================

TESSERACT_PATH = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


if os.path.exists(
    TESSERACT_PATH
):

    pytesseract.pytesseract.tesseract_cmd = (
        TESSERACT_PATH
    )

    print(
        "Tesseract OCR configured successfully."
    )

else:

    print(
        "WARNING: Tesseract OCR executable not found."
    )

    print(
        "Expected location:"
    )

    print(
        TESSERACT_PATH
    )


# ============================================================
# CONFIGURATION
# ============================================================

SUPPORTED_IMAGE_EXTENSIONS = {

    "jpg",

    "jpeg",

    "png"

}


# ============================================================
# PDF CONFIGURATION
# ============================================================

# If direct extraction is shorter than this,
# OCR fallback will be attempted.

MINIMUM_DIRECT_TEXT_LENGTH = 100


# PDF OCR resolution

PDF_OCR_SCALE = 3


# ============================================================
# CHECK TESSERACT
# ============================================================

def check_tesseract():

    """
    Check whether Tesseract OCR
    is installed and available.
    """

    try:

        version = (
            pytesseract.get_tesseract_version()
        )


        print(
            f"Tesseract OCR Version: {version}"
        )


        return True


    except Exception as error:

        print(
            "Tesseract OCR is not available."
        )

        print(
            error
        )


        return False


# ============================================================
# CLEAN EXTRACTED TEXT
# ============================================================

def clean_text(text):

    """
    Clean extracted document text.
    """

    if not text:

        return ""


    text = str(
        text
    )


    # Normalize line endings

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )


    # Remove unnecessary blank lines

    lines = []


    for line in text.split(
        "\n"
    ):

        cleaned_line = line.strip()


        if cleaned_line:

            lines.append(
                cleaned_line
            )


    return "\n".join(
        lines
    ).strip()


# ============================================================
# PREPROCESS IMAGE FOR OCR
# ============================================================

def preprocess_image(
    image
):

    """
    Improve image before OCR.

    Steps:

    - Convert to grayscale
    - Improve contrast
    - Improve brightness
    - Sharpen image
    - Increase resolution
    """

    try:

        # ----------------------------------------------------
        # FIX IMAGE ORIENTATION
        # ----------------------------------------------------

        image = ImageOps.exif_transpose(
            image
        )


        # ----------------------------------------------------
        # CONVERT TO GRAYSCALE
        # ----------------------------------------------------

        image = image.convert(
            "L"
        )


        # ----------------------------------------------------
        # AUTOCONTRAST
        # ----------------------------------------------------

        image = ImageOps.autocontrast(
            image
        )


        # ----------------------------------------------------
        # CONTRAST
        # ----------------------------------------------------

        image = ImageEnhance.Contrast(
            image
        ).enhance(
            2.0
        )


        # ----------------------------------------------------
        # BRIGHTNESS
        # ----------------------------------------------------

        image = ImageEnhance.Brightness(
            image
        ).enhance(
            1.15
        )


        # ----------------------------------------------------
        # SHARPEN
        # ----------------------------------------------------

        image = image.filter(
            ImageFilter.SHARPEN
        )


        # ----------------------------------------------------
        # RESIZE
        # ----------------------------------------------------

        width, height = image.size


        # Avoid unnecessary massive images

        if width < 3000:

            new_width = (
                width * 2
            )

            new_height = (
                height * 2
            )


            image = image.resize(

                (
                    new_width,
                    new_height
                ),

                Image.Resampling.LANCZOS

            )


        return image


    except Exception as error:

        print(
            f"Image preprocessing error: {error}"
        )


        return image


# ============================================================
# OCR IMAGE
# ============================================================

def run_ocr(
    image
):

    """
    Run OCR on processed image.
    """

    try:

        text = pytesseract.image_to_string(

            image,

            config=(
                "--oem 3 "
                "--psm 6"
            )

        )


        return clean_text(
            text
        )


    except Exception as error:

        print(
            f"OCR error: {error}"
        )


        return ""


# ============================================================
# EXTRACT TEXT FROM IMAGE
# ============================================================

def extract_text_from_image(
    file_path
):

    """
    Extract text from JPG, JPEG
    or PNG using OCR.
    """

    if not check_tesseract():

        return ""


    try:

        print(
            "Running OCR on image..."
        )


        image = Image.open(
            file_path
        )


        processed_image = (
            preprocess_image(
                image
            )
        )


        text = run_ocr(
            processed_image
        )


        print(
            f"OCR extracted "
            f"{len(text)} characters."
        )


        print(
            "OCR TEXT PREVIEW:"
        )

        print(
            text[:500]
        )


        return text


    except Exception as error:

        print(
            f"OCR image extraction error: {error}"
        )


        return ""


# ============================================================
# EXTRACT TEXT FROM NORMAL PDF
# ============================================================

def extract_text_from_pdf_direct(
    file_path
):

    """
    Extract text directly from PDF.
    """

    extracted_text = ""

    document = None


    try:

        print(
            "Trying direct PDF text extraction..."
        )


        document = fitz.open(
            file_path
        )


        for page_number in range(
            len(document)
        ):

            page = document.load_page(
                page_number
            )


            page_text = page.get_text(
                "text"
            )


            if page_text:

                extracted_text += (

                    page_text

                    + "\n"

                )


            print(

                f"PDF page "
                f"{page_number + 1} processed."

            )


    except Exception as error:

        print(
            f"PDF direct extraction error: {error}"
        )


        return ""


    finally:

        if document:

            document.close()


    extracted_text = clean_text(
        extracted_text
    )


    print(
        f"Direct PDF extraction returned "
        f"{len(extracted_text)} characters."
    )


    return extracted_text


# ============================================================
# OCR FOR SCANNED PDF
# ============================================================

def extract_text_from_scanned_pdf(
    file_path
):

    """
    Convert PDF pages to images
    and perform OCR.
    """

    if not check_tesseract():

        return ""


    extracted_text = ""

    document = None


    try:

        document = fitz.open(
            file_path
        )


        total_pages = len(
            document
        )


        print(
            f"Running OCR on "
            f"{total_pages} PDF page(s)..."
        )


        for page_number in range(
            total_pages
        ):

            page = document.load_page(
                page_number
            )


            # ------------------------------------------------
            # HIGHER RESOLUTION
            # ------------------------------------------------

            matrix = fitz.Matrix(

                PDF_OCR_SCALE,

                PDF_OCR_SCALE

            )


            pixmap = page.get_pixmap(

                matrix=matrix,

                alpha=False

            )


            image = Image.frombytes(

                "RGB",

                (
                    pixmap.width,
                    pixmap.height
                ),

                pixmap.samples

            )


            # ------------------------------------------------
            # PREPROCESS
            # ------------------------------------------------

            processed_image = (
                preprocess_image(
                    image
                )
            )


            # ------------------------------------------------
            # OCR
            # ------------------------------------------------

            page_text = run_ocr(
                processed_image
            )


            if page_text:

                extracted_text += (

                    page_text

                    + "\n"

                )


            print(

                f"OCR completed for page "
                f"{page_number + 1}/"
                f"{total_pages}"

            )


        extracted_text = clean_text(
            extracted_text
        )


        print(
            f"Total OCR extracted characters: "
            f"{len(extracted_text)}"
        )


        print(
            "OCR TEXT PREVIEW:"
        )

        print(
            extracted_text[:500]
        )


        return extracted_text


    except Exception as error:

        print(
            f"Scanned PDF OCR error: {error}"
        )


        return ""


    finally:

        if document:

            document.close()


# ============================================================
# EXTRACT TEXT FROM PDF
# ============================================================

def extract_text_from_pdf(
    file_path
):

    """
    Extract PDF text.

    First tries direct extraction.

    If extracted text is too short,
    OCR fallback is used.
    """

    # ========================================================
    # DIRECT EXTRACTION
    # ========================================================

    direct_text = (
        extract_text_from_pdf_direct(
            file_path
        )
    )


    # ========================================================
    # DIRECT EXTRACTION SUCCESS
    # ========================================================

    if len(
        direct_text
    ) >= MINIMUM_DIRECT_TEXT_LENGTH:

        print(
            "Direct PDF text extraction successful."
        )


        print(
            "TEXT PREVIEW:"
        )

        print(
            direct_text[:500]
        )


        return direct_text


    # ========================================================
    # OCR FALLBACK
    # ========================================================

    print(
        "Direct PDF text is missing or too short."
    )


    print(
        "Trying OCR on PDF..."
    )


    ocr_text = (
        extract_text_from_scanned_pdf(
            file_path
        )
    )


    # ========================================================
    # RETURN BEST RESULT
    # ========================================================

    if len(
        ocr_text
    ) > len(
        direct_text
    ):

        print(
            "Using OCR extracted text."
        )


        return ocr_text


    print(
        "Using direct extracted text."
    )


    return direct_text


# ============================================================
# EXTRACT TEXT FROM DOCX
# ============================================================

def extract_text_from_docx(
    file_path
):

    """
    Extract text from DOCX files.

    Extracts:

    - Paragraphs
    - Tables
    """

    try:

        print(
            "Extracting text from DOCX..."
        )


        document = Document(
            file_path
        )


        text_parts = []


        # ====================================================
        # PARAGRAPHS
        # ====================================================

        for paragraph in (
            document.paragraphs
        ):

            text = paragraph.text.strip()


            if text:

                text_parts.append(
                    text
                )


        # ====================================================
        # TABLES
        # ====================================================

        for table in (
            document.tables
        ):

            for row in table.rows:

                for cell in row.cells:

                    text = cell.text.strip()


                    if text:

                        text_parts.append(
                            text
                        )


        # ====================================================
        # COMBINE
        # ====================================================

        extracted_text = "\n".join(
            text_parts
        )


        extracted_text = clean_text(
            extracted_text
        )


        print(
            f"DOCX extracted "
            f"{len(extracted_text)} characters."
        )


        print(
            "TEXT PREVIEW:"
        )

        print(
            extracted_text[:500]
        )


        return extracted_text


    except Exception as error:

        print(
            f"DOCX extraction error: {error}"
        )


        return ""


# ============================================================
# MAIN FILE EXTRACTOR
# ============================================================

def extract_text_from_file(
    file_path
):

    """
    Automatically detect file type
    and extract text.
    """


    # ========================================================
    # VALIDATE FILE
    # ========================================================

    if not file_path:

        print(
            "No file path provided."
        )


        return ""


    if not os.path.exists(
        file_path
    ):

        print(
            f"File does not exist: "
            f"{file_path}"
        )


        return ""


    # ========================================================
    # GET EXTENSION
    # ========================================================

    extension = (

        os.path.splitext(
            file_path
        )[1]

        .lower()

        .replace(
            ".",
            ""
        )

    )


    print(
        "\n========================================"
    )

    print(
        f"EXTRACTING TEXT FROM: "
        f"{extension.upper()}"
    )

    print(
        f"FILE: "
        f"{os.path.basename(file_path)}"
    )

    print(
        "========================================"
    )


    # ========================================================
    # PDF
    # ========================================================

    if extension == "pdf":

        return extract_text_from_pdf(
            file_path
        )


    # ========================================================
    # DOCX
    # ========================================================

    if extension == "docx":

        return extract_text_from_docx(
            file_path
        )


    # ========================================================
    # IMAGE
    # ========================================================

    if extension in (
        SUPPORTED_IMAGE_EXTENSIONS
    ):

        return extract_text_from_image(
            file_path
        )


    # ========================================================
    # UNSUPPORTED
    # ========================================================

    print(
        f"Unsupported file type: "
        f"{extension}"
    )


    return ""


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n========================================"
    )

    print(
        "DOCUMENT TEXT EXTRACTOR TEST"
    )

    print(
        "========================================"
    )


    # ========================================================
    # CHECK OCR
    # ========================================================

    check_tesseract()


    # ========================================================
    # GET FILE
    # ========================================================

    test_file = input(

        "\nEnter full file path: "

    ).strip()


    # ========================================================
    # EXTRACT
    # ========================================================

    extracted_text = (
        extract_text_from_file(
            test_file
        )
    )


    # ========================================================
    # RESULT
    # ========================================================

    print(
        "\n========================================"
    )

    print(
        "FINAL EXTRACTED TEXT"
    )

    print(
        "========================================\n"
    )


    print(
        extracted_text
    )


    print(
        "\n========================================"
    )

    print(
        f"TOTAL CHARACTERS: "
        f"{len(extracted_text)}"
    )

    print(
        "========================================"
    )