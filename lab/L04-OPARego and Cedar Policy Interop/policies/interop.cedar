forbid(principal,action,resource) when{
    action in [Action::"delete_file", Action :: "run_command"]

};

permit(principal, action, resource) when {
    action in [Action ::"web_search", Action::"read_file"]
};