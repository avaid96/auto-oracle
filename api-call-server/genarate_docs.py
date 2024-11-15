import zipfile
from typing import List, Tuple

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from model_utils import DEFAULT_MODEL, get_llm_model


class Docx:
  def __init__(self, filepath: str) -> None:
    self.filepath = filepath
    self.zipfile = zipfile.ZipFile(filepath)
    self.content_xml = self.get_contnet_xml()

  def get_contnet_xml(self) -> str:
    filename = 'word/document.xml'
    with self.zipfile.open(filename, 'r') as f:
      return f.read().decode('utf-8')
    
  def set_content_xml(self, content: str) -> None:
    self.content_xml = content

  def save(self, output_filepath: str) -> None:
    with zipfile.ZipFile(output_filepath, 'w') as f:
      for file in self.zipfile.filelist:
        if file.filename == 'word/document.xml':
          f.writestr(file, self.content_xml.encode('utf-8'))
        else:
          f.writestr(file, self.zipfile.read(file.filename))


def get_filled_xml(input_xml: str, qa_pairs=List[Tuple[str, str]], model_name: str=DEFAULT_MODEL) -> List[str]:
  prompt_template = """
Modify the input XML of a docx to add answers asked in the document. 
Return on only the modified XML content. 
Don't add any explanation or other information in the output.

**The Question Answer pairs**

{qa_pairs_str}

**The XML content**

{input_xml}
  """
  qa_pairs_str = '\n\n'.join([f'Q:{q}\nA:{a}' for q, a in qa_pairs])
  prompt = PromptTemplate(
      input_variables=["document"], template=prompt_template
  )
  print(f'Prompt: {prompt}')
  llm_model = get_llm_model(model_name=model_name)
  chain = prompt | llm_model | StrOutputParser()
  print(f'Chain: {chain}')
  model_resp = chain.invoke(dict(qa_pairs_str=qa_pairs_str, input_xml=input_xml))
  model_resp = model_resp.strip()
  # Trim ```xml and ``` from the response
  if model_resp.startswith('```xml'):
    model_resp = model_resp[6:]
  if model_resp.endswith('```'):
    model_resp = model_resp[:-3]
  return model_resp.strip()


def fill_docx_with_qa(docx_path: str, qa_pairs: List[Tuple[str, str]], model_name: str=DEFAULT_MODEL) -> str:
  docx = Docx(docx_path)
  filled_xml = get_filled_xml(docx.content_xml, qa_pairs, model_name)
  docx.set_content_xml(filled_xml)
  out_path = docx_path.replace('.docx', '_filled.docx') 
  docx.save(out_path)
  return out_path


if __name__=='__main__':
  docx_path = "uploads/Sample RFP.docx"
  qa_pairs = [
    (
      "How can I use AI Hub to extract information from complex documents like PDFs or Excel files?", 
      "To extract information, sign up at aihub.instabase.com to receive free credits. Create a new project in the Converse section, add your documents (PDFs, Excels, etc.), and start asking questions about the content. AI Hub can handle various file types and even span queries across multiple documents."
    ),
    (
      "What is the process for creating a chatbot that converses with documents in AI Hub?",
      "In AI Hub, after setting up a Converse project and adding documents, you can test some queries. Once satisfied with the results, create a chatbot from the project. This chatbot can be shared, allowing users to interact with it to get answers based on the document information, without seeing the original documents."
    ),
    (
      "How do I deploy custom apps for document understanding in Instabase AI Hub?",
      "Use the Build feature in AI Hub to deploy custom apps. Start by creating a Build project, uploading documents, and specifying fields for extraction. Verify and adjust the results as needed, then deploy the app with a single click, making it available for others to use with their own documents. Prebuilt apps, like Passport and W2, are also available for use."
    )
  ]
  out_path = fill_docx_with_qa(docx_path, qa_pairs)
  print (out_path)