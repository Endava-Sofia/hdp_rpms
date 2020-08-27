# Ansible playbook to build rpms from scrach

## Requirements
- ansible 2.9
- boto & boto3
- access to bucket and ec2

## Run
```ansible-playbook -i hosts main.yaml```

## Notes
Change the required vars if you are not running against default environment
