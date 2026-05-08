from agent_os import PolicyEngine, SyscallType,KernelSpace, AgentKernelPanic
import os
import asyncio
def web_search(query:str)->str:
    return f"mock web_search of {query}"

def delete_file(path:str)->str:
    return f"delete file at {path}"
    
async def main():
    agent_id="agent1"
    policy=PolicyEngine()
    policy.add_constraint(role=agent_id,
                          allowed_tools=["web_search", "syscall_sys_checkpolicy"]
                          )
    policy.freeze()
    
    kernel=KernelSpace(policy_engine=policy)
    ctx=kernel.create_agent_context(agent_id)
    kernel.register_tool("web_search",web_search)
    kernel.register_tool("delete_file",delete_file)
    
    pre_allow= await ctx.syscall(
        SyscallType.SYS_CHECKPOLICY,
        action="web_search",
        args={"query":"agent governance toolkit"}
    )
    print("PRECHECK web_search", pre_allow.success,pre_allow.return_value, pre_allow.error_message)
    
    pre_block= await ctx.syscall(
        SyscallType.SYS_CHECKPOLICY,
        action="delete_file",
        args={"path":r"C:\temp\demo.txt"}
    )
    print("PRECHECK delete_file:", pre_block.success,pre_block.return_value,pre_block.error_message)
    
    allowed_exec=await ctx.syscall(
        SyscallType.SYS_EXEC,
        tool="web_search",
        args={"query":"OWASP Agentic top 10"}
    )
    print("EXEC web_search", allowed_exec.success,allowed_exec.return_value,allowed_exec.error_message)
    
    blocked_ok=False
    
    try:
        blocked_exec= await ctx.syscall(
            SyscallType.SYS_EXEC,
            tool="delete_file",
            args={"path":r"C:\temp\demo.txt"}
        )
        print("EXEC delete_file:", blocked_exec.success,blocked_exec.return_value,blocked_exec.error_message)
        
        blocked_ok=not blocked_exec.success
    
    except AgentKernelPanic as exec:
        print("EXEC delete_file blocked with kernel panic:",exec)
        blocked_ok=True
    
    assert allowed_exec.success,"web_search should eb allowed"
    assert blocked_ok,"delete_file should be block"

    
if __name__=="__main__":
    asyncio.run(main())