"""
Microsoft Purview Workflow CLI Commands
Provides command-line interface for workflow management operations
"""

import click
import json
from rich.console import Console

console = Console()


@click.group()
def workflow():
    """Manage workflows and approval processes in Microsoft Purview."""
    pass


# ========== Basic Workflow Management Commands ==========


@workflow.command()
@click.pass_context
def list(ctx):
    """List all workflows."""
    try:
        if ctx.obj and ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: workflow list command[/yellow]")
            console.print("[green]✓ Mock workflow list completed successfully[/green]")
            return

        from purviewcli.client._workflow import Workflow

        args = {}
        workflow_client = Workflow()
        result = workflow_client.workflowListWorkflows(args)

        if result:
            console.print("[green]✓ Workflow list completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ No workflows found[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error executing workflow list: {str(e)}[/red]")


@workflow.command()
@click.option("--workflow-id", required=True, help="Workflow ID")
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="JSON file with workflow definition",
)
@click.pass_context
def create(ctx, workflow_id, payload_file):
    """Create a new workflow."""
    try:
        if ctx.obj and ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: workflow create command[/yellow]")
            console.print(f"[dim]Workflow ID: {workflow_id}[/dim]")
            console.print(f"[dim]Payload File: {payload_file}[/dim]")
            console.print("[green]✓ Mock workflow create completed successfully[/green]")
            return

        from purviewcli.client._workflow import Workflow

        args = {"--workflowId": workflow_id, "--payloadFile": payload_file}
        workflow_client = Workflow()
        result = workflow_client.workflowCreateWorkflow(args)

        if result:
            console.print("[green]✓ Workflow create completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Workflow create completed with no result[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error executing workflow create: {str(e)}[/red]")


@workflow.command()
@click.option("--workflow-id", required=True, help="Workflow ID")
@click.pass_context
def get(ctx, workflow_id):
    """Get a specific workflow."""
    try:
        if ctx.obj and ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: workflow get command[/yellow]")
            console.print(f"[dim]Workflow ID: {workflow_id}[/dim]")
            console.print("[green]✓ Mock workflow get completed successfully[/green]")
            return

        from purviewcli.client._workflow import Workflow

        args = {"--workflowId": workflow_id}
        workflow_client = Workflow()
        result = workflow_client.workflowGetWorkflow(args)

        if result:
            console.print("[green]✓ Workflow get completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Workflow not found[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error executing workflow get: {str(e)}[/red]")


@workflow.command()
@click.option("--workflow-id", required=True, help="Workflow ID")
@click.option(
    "--payload-file", type=click.Path(exists=True), help="JSON file with execution parameters"
)
@click.pass_context
def execute(ctx, workflow_id, payload_file):
    """Execute a workflow."""
    try:
        if ctx.obj and ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: workflow execute command[/yellow]")
            console.print(f"[dim]Workflow ID: {workflow_id}[/dim]")
            if payload_file:
                console.print(f"[dim]Payload File: {payload_file}[/dim]")
            console.print("[green]✓ Mock workflow execute completed successfully[/green]")
            return

        from purviewcli.client._workflow import Workflow

        args = {"--workflowId": workflow_id}
        if payload_file:
            args["--payloadFile"] = payload_file
        workflow_client = Workflow()
        result = workflow_client.workflowExecuteWorkflow(args)

        if result:
            console.print("[green]✓ Workflow execute completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Workflow execute completed with no result[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error executing workflow: {str(e)}[/red]")


@workflow.command()
@click.option("--workflow-id", required=True, help="Workflow ID")
@click.pass_context
def executions(ctx, workflow_id):
    """List workflow executions."""
    try:
        if ctx.obj and ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: workflow executions command[/yellow]")
            console.print(f"[dim]Workflow ID: {workflow_id}[/dim]")
            console.print("[green]✓ Mock workflow executions completed successfully[/green]")
            return

        from purviewcli.client._workflow import Workflow

        args = {"--workflowId": workflow_id}
        workflow_client = Workflow()
        result = workflow_client.workflowListWorkflowExecutions(args)

        if result:
            console.print("[green]✓ Workflow executions list completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ No workflow executions found[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error listing workflow executions: {str(e)}[/red]")


# ========== Approval Commands ==========


@workflow.command()
@click.option("--status", help="Filter by approval status")
@click.option("--assigned-to", help="Filter by assignee")
@click.pass_context
def approvals(ctx, status, assigned_to):
    """List approval requests."""
    try:
        if ctx.obj and ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: workflow approvals command[/yellow]")
            if status:
                console.print(f"[dim]Status Filter: {status}[/dim]")
            if assigned_to:
                console.print(f"[dim]Assigned To: {assigned_to}[/dim]")
            console.print("[green]✓ Mock workflow approvals completed successfully[/green]")
            return

        from purviewcli.client._workflow import Workflow

        args = {}
        if status:
            args["--status"] = status
        if assigned_to:
            args["--assignedTo"] = assigned_to
        workflow_client = Workflow()
        result = workflow_client.workflowGetApprovalRequests(args)

        if result:
            console.print("[green]✓ Approval requests list completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ No approval requests found[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error listing approval requests: {str(e)}[/red]")


@workflow.command()
@click.option("--request-id", required=True, help="Approval request ID")
@click.option("--comments", help="Approval comments")
@click.pass_context
def approve(ctx, request_id, comments):
    """Approve a request."""
    try:
        if ctx.obj and ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: workflow approve command[/yellow]")
            console.print(f"[dim]Request ID: {request_id}[/dim]")
            if comments:
                console.print(f"[dim]Comments: {comments}[/dim]")
            console.print("[green]✓ Mock workflow approve completed successfully[/green]")
            return

        from purviewcli.client._workflow import Workflow

        args = {"--requestId": request_id}
        if comments:
            args["--comments"] = comments
        workflow_client = Workflow()
        result = workflow_client.workflowApproveRequest(args)

        if result:
            console.print("[green]✓ Request approved successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Request approval completed with no result[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error approving request: {str(e)}[/red]")


@workflow.command()
@click.option("--request-id", required=True, help="Approval request ID")
@click.option("--comments", help="Rejection comments")
@click.pass_context
def reject(ctx, request_id, comments):
    """Reject a request."""
    try:
        if ctx.obj and ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: workflow reject command[/yellow]")
            console.print(f"[dim]Request ID: {request_id}[/dim]")
            if comments:
                console.print(f"[dim]Comments: {comments}[/dim]")
            console.print("[green]✓ Mock workflow reject completed successfully[/green]")
            return

        from purviewcli.client._workflow import Workflow

        args = {"--requestId": request_id}
        if comments:
            args["--comments"] = comments
        workflow_client = Workflow()
        result = workflow_client.workflowRejectRequest(args)

        if result:
            console.print("[green]✓ Request rejected successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Request rejection completed with no result[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error rejecting request: {str(e)}[/red]")


# ========== Template Commands ==========


@workflow.command()
@click.pass_context
def templates(ctx):
    """List available workflow templates."""
    try:
        if ctx.obj and ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: workflow templates command[/yellow]")
            console.print("[green]✓ Mock workflow templates completed successfully[/green]")
            return

        from purviewcli.client._workflow import Workflow

        args = {}
        workflow_client = Workflow()
        result = workflow_client.workflowListWorkflowTemplates(args)

        if result:
            console.print("[green]✓ Workflow templates list completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ No workflow templates found[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error listing workflow templates: {str(e)}[/red]")


@workflow.command()
@click.option("--template-id", required=True, help="Template ID")
@click.pass_context
def template(ctx, template_id):
    """Get a specific workflow template."""
    try:
        if ctx.obj and ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: workflow template command[/yellow]")
            console.print(f"[dim]Template ID: {template_id}[/dim]")
            console.print("[green]✓ Mock workflow template completed successfully[/green]")
            return

        from purviewcli.client._workflow import Workflow

        args = {"--templateId": template_id}
        workflow_client = Workflow()
        result = workflow_client.workflowGetWorkflowTemplate(args)

        if result:
            console.print("[green]✓ Workflow template get completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Workflow template not found[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error getting workflow template: {str(e)}[/red]")


# ========== Validation Commands ==========


@workflow.command()
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="JSON file with workflow definition to validate",
)
@click.pass_context
def validate(ctx, payload_file):
    """Validate a workflow definition."""
    try:
        if ctx.obj and ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: workflow validate command[/yellow]")
            console.print(f"[dim]Payload File: {payload_file}[/dim]")
            console.print("[green]✓ Mock workflow validate completed successfully[/green]")
            return

        from purviewcli.client._workflow import Workflow

        args = {"--payloadFile": payload_file}
        workflow_client = Workflow()
        result = workflow_client.workflowValidateWorkflow(args)

        if result:
            console.print("[green]✓ Workflow validation completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Workflow validation completed with no result[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error validating workflow: {str(e)}[/red]")


if __name__ == "__main__":
    workflow()
