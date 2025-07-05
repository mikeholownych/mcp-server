# MCP-server

This is the MCP-server application, running on FastAPI and Docker.

## New Enhancement

### /api/enhancement-rollback

This endpoint attempts a rollback of a failed enhancement by reverting to the last stable main, redeploying, and updating the enhancement status/log.

#### Example usage:


POST /api/enhancement-rollback
{
  "enhancement_id": 1
}

