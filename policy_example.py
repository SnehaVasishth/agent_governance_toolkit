from agent_os.lite import govern
from agent_os import KernelSpace
from agent_control_plane
# Define capability model
capabilities = govern(
    allow=["web_search", "read_file", "send_email"],
    deny=["execute_code", "delete_file"],   

    max_calls=10,
)
kernel= KernelSpace(
    
)

 
# Create policy engine
decision = capabilities.evaluate(action="delete_file",context="Delete database")
print(decision)
