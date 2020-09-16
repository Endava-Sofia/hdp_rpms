# Ansible playbook to build rpms from scrach

## Requirements
- ansible 2.9
- boto & boto3
- access to bucket and ec2

## Run
```ansible-playbook -i hosts main.yaml```

You can build none single or some/all rpms depending on the tags you provide to the playbook
The tags sypported are `all`, `samhain`, `mod_jk`, `java` and `efs-utils`

Example build only java
```ansible-playbook -i hosts main.yaml --tags "java" ```

## Notes
Change the required vars if you are not running against default environment
