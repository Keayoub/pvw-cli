"""
Microsoft Purview Workflow Client - Complete API Coverage
Handles Workflow Management, Approval Processes, and Business Process Automation
"""

from .endpoint import Endpoint, decorator, get_json
from .endpoints import ENDPOINTS, format_endpoint, get_api_version_params

class Workflow(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'workflow'

    # ========== Workflow Management ==========
    
    @decorator
    def workflowListWorkflows(self, args):
        """List all workflows"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['workflow']['list_workflows']
        self.params = get_api_version_params('workflow')

    @decorator
    def workflowCreateWorkflow(self, args):
        """Create a new workflow"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['create_workflow'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def workflowGetWorkflow(self, args):
        """Get a specific workflow"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['get_workflow'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')

    @decorator
    def workflowUpdateWorkflow(self, args):
        """Update an existing workflow"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['update_workflow'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def workflowDeleteWorkflow(self, args):
        """Delete a workflow"""
        self.method = 'DELETE'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['delete_workflow'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')

    # ========== Workflow Execution ==========
    
    @decorator
    def workflowExecuteWorkflow(self, args):
        """Execute a workflow"""
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['execute_workflow'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')
        self.payload = get_json(args, '--payloadFile') if args.get('--payloadFile') else {}

    @decorator
    def workflowGetWorkflowExecution(self, args):
        """Get workflow execution details"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_execution'], 
                                      workflowId=args['--workflowId'],
                                      executionId=args['--executionId'])
        self.params = get_api_version_params('workflow')

    @decorator
    def workflowListWorkflowExecutions(self, args):
        """List workflow executions"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_executions'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')

    @decorator
    def workflowCancelWorkflowExecution(self, args):
        """Cancel a workflow execution"""
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['cancel_workflow_execution'], 
                                      workflowId=args['--workflowId'],
                                      executionId=args['--executionId'])
        self.params = get_api_version_params('workflow')

    # ========== Workflow Runs and History ==========
    
    @decorator
    def workflowGetWorkflowRuns(self, args):
        """Get workflow runs"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_runs'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')
        if args.get('--status'):
            self.params['status'] = args['--status']
        if args.get('--startTime'):
            self.params['startTime'] = args['--startTime']
        if args.get('--endTime'):
            self.params['endTime'] = args['--endTime']

    @decorator
    def workflowGetWorkflowRunDetails(self, args):
        """Get detailed workflow run information"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_run'], 
                                      workflowId=args['--workflowId'],
                                      runId=args['--runId'])
        self.params = get_api_version_params('workflow')

    @decorator
    def workflowGetWorkflowHistory(self, args):
        """Get workflow execution history"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_history'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')

    # ========== Workflow Templates ==========
    
    @decorator
    def workflowListWorkflowTemplates(self, args):
        """List available workflow templates"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['workflow']['workflow_templates']
        self.params = get_api_version_params('workflow')

    @decorator
    def workflowGetWorkflowTemplate(self, args):
        """Get a specific workflow template"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_template'], 
                                      templateId=args['--templateId'])
        self.params = get_api_version_params('workflow')

    @decorator
    def workflowCreateWorkflowFromTemplate(self, args):
        """Create a workflow from a template"""
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['create_from_template'], 
                                      templateId=args['--templateId'])
        self.params = get_api_version_params('workflow')
        self.payload = get_json(args, '--payloadFile')

    # ========== Workflow Tasks and Steps ==========
    
    @decorator
    def workflowGetWorkflowTasks(self, args):
        """Get tasks for a workflow"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_tasks'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')

    @decorator
    def workflowGetWorkflowTask(self, args):
        """Get a specific workflow task"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_task'], 
                                      workflowId=args['--workflowId'],
                                      taskId=args['--taskId'])
        self.params = get_api_version_params('workflow')

    @decorator
    def workflowUpdateWorkflowTask(self, args):
        """Update a workflow task"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_task'], 
                                      workflowId=args['--workflowId'],
                                      taskId=args['--taskId'])
        self.params = get_api_version_params('workflow')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def workflowCompleteWorkflowTask(self, args):
        """Complete a workflow task"""
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['complete_task'], 
                                      workflowId=args['--workflowId'],
                                      taskId=args['--taskId'])
        self.params = get_api_version_params('workflow')
        self.payload = get_json(args, '--payloadFile') if args.get('--payloadFile') else {}

    # ========== Approval Workflows ==========
    
    @decorator
    def workflowCreateApprovalWorkflow(self, args):
        """Create an approval workflow"""
        self.method = 'POST'
        self.endpoint = ENDPOINTS['workflow']['create_approval_workflow']
        self.params = get_api_version_params('workflow')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def workflowGetApprovalRequests(self, args):
        """Get approval requests"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['workflow']['approval_requests']
        self.params = get_api_version_params('workflow')
        if args.get('--status'):
            self.params['status'] = args['--status']
        if args.get('--assignedTo'):
            self.params['assignedTo'] = args['--assignedTo']

    @decorator
    def workflowGetApprovalRequest(self, args):
        """Get a specific approval request"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['approval_request'], 
                                      requestId=args['--requestId'])
        self.params = get_api_version_params('workflow')

    @decorator
    def workflowApproveRequest(self, args):
        """Approve a request"""
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['approve_request'], 
                                      requestId=args['--requestId'])
        self.params = get_api_version_params('workflow')
        self.payload = {
            'decision': 'approved',
            'comments': args.get('--comments', '')
        }

    @decorator
    def workflowRejectRequest(self, args):
        """Reject a request"""
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['reject_request'], 
                                      requestId=args['--requestId'])
        self.params = get_api_version_params('workflow')
        self.payload = {
            'decision': 'rejected',
            'comments': args.get('--comments', '')
        }

    # ========== Workflow Triggers ==========
    
    @decorator
    def workflowListWorkflowTriggers(self, args):
        """List workflow triggers"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_triggers'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')

    @decorator
    def workflowCreateWorkflowTrigger(self, args):
        """Create a workflow trigger"""
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['create_trigger'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def workflowDeleteWorkflowTrigger(self, args):
        """Delete a workflow trigger"""
        self.method = 'DELETE'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_trigger'], 
                                      workflowId=args['--workflowId'],
                                      triggerId=args['--triggerId'])
        self.params = get_api_version_params('workflow')

    # ========== Workflow Actions and Conditions ==========
    
    @decorator
    def workflowGetWorkflowActions(self, args):
        """Get available workflow actions"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['workflow']['workflow_actions']
        self.params = get_api_version_params('workflow')

    @decorator
    def workflowGetWorkflowConditions(self, args):
        """Get available workflow conditions"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['workflow']['workflow_conditions']
        self.params = get_api_version_params('workflow')

    @decorator
    def workflowValidateWorkflow(self, args):
        """Validate a workflow definition"""
        self.method = 'POST'
        self.endpoint = ENDPOINTS['workflow']['validate_workflow']
        self.params = get_api_version_params('workflow')
        self.payload = get_json(args, '--payloadFile')

    # ========== Workflow Monitoring and Metrics ==========
    
    @decorator
    def workflowGetWorkflowMetrics(self, args):
        """Get workflow performance metrics"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_metrics'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')
        if args.get('--timeRange'):
            self.params['timeRange'] = args['--timeRange']

    @decorator
    def workflowGetWorkflowLogs(self, args):
        """Get workflow execution logs"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_logs'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')
        if args.get('--executionId'):
            self.params['executionId'] = args['--executionId']

    @decorator
    def workflowExportWorkflowLogs(self, args):
        """Export workflow logs"""
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['export_logs'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')
        self.payload = {
            'format': args.get('--format', 'json'),
            'startTime': args.get('--startTime'),
            'endTime': args.get('--endTime')
        }

    # ========== Workflow Scheduling ==========
    
    @decorator
    def workflowScheduleWorkflow(self, args):
        """Schedule a workflow for execution"""
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['schedule_workflow'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def workflowGetWorkflowSchedules(self, args):
        """Get workflow schedules"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_schedules'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')

    @decorator
    def workflowDeleteWorkflowSchedule(self, args):
        """Delete a workflow schedule"""
        self.method = 'DELETE'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_schedule'], 
                                      workflowId=args['--workflowId'],
                                      scheduleId=args['--scheduleId'])
        self.params = get_api_version_params('workflow')

    # ========== Advanced Workflow Features ==========
    
    @decorator
    def workflowCreateWorkflowVariable(self, args):
        """Create a workflow variable"""
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_variables'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def workflowGetWorkflowVariables(self, args):
        """Get workflow variables"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_variables'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')

    @decorator
    def workflowCreateWorkflowVersion(self, args):
        """Create a new version of a workflow"""
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_versions'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def workflowGetWorkflowVersions(self, args):
        """Get workflow versions"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['workflow_versions'], 
                                      workflowId=args['--workflowId'])
        self.params = get_api_version_params('workflow')

    # ========== Workflow Integration ==========
    
    @decorator
    def workflowGetWorkflowIntegrations(self, args):
        """Get available workflow integrations"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['workflow']['workflow_integrations']
        self.params = get_api_version_params('workflow')

    @decorator
    def workflowConfigureIntegration(self, args):
        """Configure a workflow integration"""
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['configure_integration'], 
                                      workflowId=args['--workflowId'],
                                      integrationType=args['--integrationType'])
        self.params = get_api_version_params('workflow')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def workflowTestIntegration(self, args):
        """Test a workflow integration"""
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['workflow']['test_integration'], 
                                      workflowId=args['--workflowId'],
                                      integrationType=args['--integrationType'])
        self.params = get_api_version_params('workflow')
        self.payload = get_json(args, '--payloadFile') if args.get('--payloadFile') else {}
