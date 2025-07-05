import os
import jwt
import requests
from time import time
from fastapi import HTTPException

class GitHubIntegration:
    def __init__(self):
        self.app_id = os.getenv('GITHUB_APP_ID')
        self.private_key = os.getenv('GITHUB_APP_PRIVATE_KEY')
        self.installation_id = os.getenv('GITHUB_APP_INSTALLATION_ID')
        if not self.app_id or not self.private_key or not self.installation_id:
            raise EnvironmentError('Missing GitHub App configuration')

    def generate_jwt(self):
        payload = {
            'iat': int(time()),
            'exp': int(time()) + 600,
            'iss': self.app_id
        }
        headers = {
            'alg': 'RS256'
        }
        jwt_token = jwt.encode(payload, self.private_key, algorithm='RS256', headers=headers)
        return jwt_token

    def get_installation_token(self):
        jwt_token = self.generate_jwt()
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.post(
            f'https://api.github.com/app/installations/{self.installation_id}/access_tokens',
            headers=headers
        )
        if response.ok:
            return response.json()['token']
        raise HTTPException(status_code=response.status_code, detail='Failed to get installation token')

    def perform_github_action(self, repo_name, action):
        token = self.get_installation_token()
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        # Example action logic (e.g., list PRs)
        if action == 'list_prs':
            response = requests.get(
                f'https://api.github.com/repos/{repo_name}/pulls',
                headers=headers
            )
            if response.ok:
                return response.json()
        raise HTTPException(status_code=response.status_code, detail=f'GitHub action {action} failed')

# Example usage
# github_integration = GitHubIntegration()
# prs = github_integration.perform_github_action('user/repo', 'list_prs')
# print(prs)
