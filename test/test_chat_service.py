from services.pdf_chat_service import PdfChatService
from test.utils.utils import file_to_bytes
import shutil

test_db_dir = "./test/test_db"

def initialize_pdf_service(session_id: str) -> PdfChatService:
    service = PdfChatService()
    file_path = "./test/fixtures/EduTrack_FAQ_assignment.pdf"
    file_bytes = file_to_bytes(file_path)
    service.process_uploaded_pdf(session_id=session_id, contents=file_bytes, db_dir=test_db_dir)

    return service

def test_answer_query_should_return_answer_relevant_to_document():
    session_id = "1234"
    service = initialize_pdf_service(session_id)
    result = service.answer_query(session_id, "Can I self host Edutrack?")

    assert "yes" in result.lower()

def test_answer_should_be_chat_history_relevant():
    session_id = "1234"
    keyword = "self host"
    service = initialize_pdf_service(session_id)
    service.answer_query(session_id, f"Can I {keyword} Edutrack?")
    service.answer_query(session_id, "Can EduTrack be used in hybrid or blended learning models?")
    result = service.answer_query(session_id, "Do you remeber what did I first asked you?")

    session_messages = service.session_store[session_id].messages
    assert len(session_messages) != 0
    assert "self" in result.lower() and "host" in result.lower()
