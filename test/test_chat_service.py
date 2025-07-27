from services.pdf_chat_service import PdfChatService
from test.utils.utils import file_to_bytes

def initialize_pdf_service(session_id: str) -> PdfChatService:
    service = PdfChatService()
    file_path = "./test/fixtures/EduTrack_FAQ_assignment.pdf"
    file_bytes = file_to_bytes(file_path)
    service.process_uploaded_pdf(session_id=session_id, contents=file_bytes, db_dir="./test/test_db")

    return service

def test_answer_query_should_return_answer_relevant_to_document():
    session_id = "1234"
    service = initialize_pdf_service(session_id)
    result = service.answer_query(session_id, "Can I self host Edutrack?")

    assert "yes" in result.lower()
