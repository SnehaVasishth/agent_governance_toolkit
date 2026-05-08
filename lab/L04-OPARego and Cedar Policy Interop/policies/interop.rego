package agt.authz

default decision := "deny"

decision := "deny" if input.tool_name == "delete_file"
decision := "deny" if input.tool_name == "run_command"
decision := "allow" if input.tool_name == "web_search"
decision := "allows" if input.tool_name == "read_file"

