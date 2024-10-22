from aihub.api.batches_api import BatchesApi
from aihub.api.conversations_api import ConversationsApi
from aihub.api.runs_api import RunsApi
from aihub.api_client import ApiClient
from aihub.api.queries_api import QueriesApi


class AIHub:

  def __init__(self,
               api_key,
               ib_context=None,
               api_root='https://aihub.instabase.com/api',
               debug=False):
    self.client = ApiClient()
    self.client.configuration.host = api_root
    self.client.configuration.access_token = api_key
    self.client.configuration.debug = debug
    self.batches = self.Batches(BatchesApi(self.client), ib_context)
    self.conversations = self.Conversations(
        ConversationsApi(self.client), ib_context)
    self.apps = self.Apps(RunsApi(self.client), ib_context)
    self.queries = self.Queries(QueriesApi(self.client), ib_context)

  class Batches:

    def __init__(self, api_instance, ib_context):
      self.api_instance = api_instance
      self.ib_context = ib_context

    def create(self, name, workspace=None):
      batch = self.api_instance.create_batch(
          {
              'name': name,
              'workspace': workspace
          }, ib_context=self.ib_context)
      return batch

    def list(self, workspace=None, username=None, limit=None, offset=None):
      response = self.api_instance.list_batches(
          workspace=workspace,
          username=username,
          limit=limit,
          offset=offset,
          ib_context=self.ib_context)
      return response

    def get(self, batch_id):
      response = self.api_instance.get_batch(
          batch_id, ib_context=self.ib_context)
      return response

    def delete(self, batch_id):
      response = self.api_instance.delete_batch(
          batch_id, ib_context=self.ib_context)
      return response

    def add_file(self, batch_id, file_name, file):
      self.api_instance.add_file_to_batch(
          batch_id, file_name, file.read(), ib_context=self.ib_context)

    def delete_file(self, batch_id, file_name):
      response = self.api_instance.delete_file_from_batch(
          batch_id, file_name, ib_context=self.ib_context)
      return response

    def poll_job(self, job_id):
      response = self.api_instance.poll_batches_job(
          job_id, ib_context=self.ib_context)
      return response

  class Conversations:

    def __init__(self, api_instance, ib_context):
      self.api_instance = api_instance
      self.ib_context = ib_context

    def create(self,
               name,
               description=None,
               files=[],
               org=None,
               workspace=None,
               enable_object_detection=None):
      response = self.api_instance.create_conversation(
          name=name,
          description=description,
          files=files,
          org=org,
          workspace=workspace,
          enable_object_detection=enable_object_detection,
          ib_context=self.ib_context)
      return response

    def status(self, conversation_id):
      status = self.api_instance.get_conversation(
          conversation_id, ib_context=self.ib_context)
      return status

    def update(self, conversation_id, name=None, description=None):
      response = self.api_instance.update_conversation(
          conversation_id,
          name=name,
          description=description,
          ib_context=self.ib_context)
      return response

    def delete(self, conversation_id):
      response = self.api_instance.delete_conversation(
          conversation_id, ib_context=self.ib_context)
      return response

    def list(self):
      conversations = self.api_instance.list_conversations(
          ib_context=self.ib_context)
      return conversations

    def converse(self,
                 conversation_id,
                 question,
                 document_ids,
                 mode='default'):
      answer = self.api_instance.converse(
          conversation_id, {
              'question': question,
              'document_ids': document_ids,
              'mode': mode
          },
          ib_context=self.ib_context)
      return answer

    def add_documents(self, conversation_id, files, process_files=True):
      response = self.api_instance.add_documents_to_conversation(
          conversation_id,
          files,
          process_files=process_files,
          ib_context=self.ib_context)
      return response

    def delete_documents(self, conversation_id, ids):
      response = self.api_instance.delete_documents_from_conversation(
          conversation_id, ids=ids, ib_context=self.ib_context)
      return response

    def get_document_metadata(self, conversation_id, document_id):
      response = self.api_instance.get_conversation_document_metadata(
          conversation_id, document_id, ib_context=self.ib_context)
      return response

  class Runs:

    def __init__(self, api_instance, ib_context):
      self.api_instance = api_instance
      self.ib_context = ib_context

    def run(self,
            app_name=None,
            app_id=None,
            files=[],
            owner=None,
            settings=None):
      results = self.api_instance.run_app_sync(
          app_name=app_name,
          app_id=app_id,
          files=files,
          owner=owner,
          settings=settings,
          ib_context=self.ib_context)
      return results

    def create(self,
               app_name=None,
               app_id=None,
               batch_id=None,
               input_dir=None,
               output_dir=None,
               owner=None,
               settings=None):
      # Validate that one of batch_id or input_dir is provided
      if not batch_id and not input_dir:
        raise ValueError("Either batch_id or input_dir is required.")

      # Construct the dictionary with only the set values
      run_details = {}
      if app_name:
        run_details['app_name'] = app_name
      elif app_id:  # Use elif because only one of them needs to be set
        run_details['app_id'] = app_id

      if batch_id:
        run_details['batch_id'] = batch_id
      elif input_dir:  # Use elif for the same reason
        run_details['input_dir'] = input_dir

      if output_dir is not None:
        run_details['output_dir'] = output_dir

      if settings is not None:
        run_details['settings'] = settings

      if owner is not None:
        run_details['owner'] = owner

      # Call run_app with the constructed dictionary
      run = self.api_instance.run_app(run_details, ib_context=self.ib_context)
      return run

    def status(self, run_id):
      status = self.api_instance.get_run_status(
          run_id, ib_context=self.ib_context)
      return status

    def results(self,
                run_id,
                file_offset=None,
                include_confidence_scores=False,
                include_source_info=False,
                include_review_results=False,
                include_validation_results=False):
      results = self.api_instance.get_run_results(
          run_id=run_id,
          file_offset=file_offset,
          include_confidence_scores=include_confidence_scores,
          include_source_info=include_source_info,
          include_review_results=include_review_results,
          include_validation_results=include_validation_results,
          ib_context=self.ib_context)
      return results

  class DeploymentRuns:

    def __init__(self, api_instance, ib_context):
      self.api_instance = api_instance
      self.ib_context = ib_context

    def create(self,
               deployment_id,
               batch_id=None,
               input_dir=None,
               version=None,
               output_workspace=None,
               output_dir=None,
               settings=None):
      # Validate that one of batch_id or input_dir is provided
      if not batch_id and not input_dir:
        raise ValueError("Either batch_id or input_dir is required.")

      # Construct the dictionary with only the set values
      run_details = {}
      if batch_id:
        run_details['batch_id'] = batch_id
      elif input_dir:  # Use elif for the same reason
        run_details['input_dir'] = input_dir

      if version:
        run_details['version'] = version

      if output_workspace:
        run_details['output_workspace'] = output_workspace

      if output_dir:
        run_details['output_dir'] = output_dir

      if settings:
        run_details['settings'] = settings

      run = self.api_instance.run_deployment(
          deployment_id, run_details, ib_context=self.ib_context)
      return run

  class Deployments:

    def __init__(self, api_instance, ib_context):
      self.api_instance = api_instance
      self.ib_context = ib_context
      self.runs = AIHub.DeploymentRuns(api_instance, ib_context)

  class Apps:

    def __init__(self, api_instance, ib_context):
      self.ib_context = ib_context
      self.runs = AIHub.Runs(api_instance, ib_context)
      self.deployments = AIHub.Deployments(api_instance, ib_context)

  class Queries:

    def __init__(self, api_instance, ib_context):
      self.api_instance = api_instance
      self.ib_context = ib_context

    def run(self,
            query,
            source_app,
            include_source_info=False,
            model_name='multistep-lite'):
      raise_query_request = {
          'query': query,
          'source_app': source_app,
          'include_source_info': include_source_info,
          'model_name': model_name
      }
      response = self.api_instance.run_query(
          raise_query_request, ib_context=self.ib_context)
      return response

    def status(self, query_id):
      status = self.api_instance.get_query_status(
          query_id, ib_context=self.ib_context)
      return status
