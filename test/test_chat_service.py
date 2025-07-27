from services.pdf_chat_service import PdfChatService
from test.utils.utils import file_to_bytes
from ragas import EvaluationDataset, evaluate
from ragas.llms import LangchainLLMWrapper
from langchain_ollama import OllamaLLM
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness
import pprint

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

# Tests overall metrics using ragas
def test_overall_pdf_rag_service():
    session_id = "1234"
    service = initialize_pdf_service(session_id)

    sample_queries = [
        "How often is data updated in the system?",
        "How is pricing structured?",
        "Where can users learn about new EduTrack features?",
        "Is there a self-hosted version of EduTrack?",
    ]

    expected_responses = [
        "Data is refreshed every hour by default. Real-time syncing options are available for premium clients.",
        "Pricing is based on the number of enrolled learners per year. Tiered pricing and volume discounts are available for larger institutions.",
        "Feature updates are published via in-app announcements, email newsletters, and the EduTrack Knowledge Base.",
        "Yes. EduTrack offers both cloud-hosted SaaS and on-premise deployments for institutions with specific data residency needs.",
    ]

    dataset = []

    for query, reference in zip(sample_queries, expected_responses):
        relevant_docs = service.get_retriever(session_id).invoke(query)
        response = service.answer_query(session_id, query)
        # Extract the page_content from Document objects to get strings
        retrieved_contexts = [doc.page_content for doc in relevant_docs]
        dataset.append(
            {
                "user_input":query,
                "retrieved_contexts":retrieved_contexts,
                "response":response,
                "reference":reference
            }
        )

    evaluation_dataset = EvaluationDataset.from_list(dataset)
    llm = OllamaLLM(model="gemma3:4b")
    evaluator_llm = LangchainLLMWrapper(llm)

    result = evaluate(
        dataset=evaluation_dataset,
        metrics=[LLMContextRecall(), Faithfulness(), FactualCorrectness()], 
        llm=evaluator_llm, 
        batch_size=4
    )

    pprint.pprint(result.scores)