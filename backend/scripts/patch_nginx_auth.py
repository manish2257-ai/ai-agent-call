import os

def patch():
    # 1. Patch Lua user_auth_verification
    lua_path = "/etc/nginx/user_auth_verification.lua"
    if os.path.exists(lua_path):
        with open(lua_path, "r") as f:
            content = f.read()
        target = "if ngx.var.host == \"localhost\" then\n  return\nend"
        replacement = """if ngx.var.host == \"localhost\" then
  return
end

-- Allow unauthenticated public access for Exotel telephony and health endpoints
local uri = ngx.var.uri
if uri == \"/health\" or uri == \"/ws/media-stream\" or string.find(uri, \"^/api/voice/exotel/\") then
  return
end"""
        if target in content and "Allow unauthenticated public access" not in content:
            with open(lua_path, "w") as f:
                f.write(content.replace(target, replacement, 1))

    # 2. Patch timeouts in nginx.conf.template
    tpl_path = "/etc/nginx/nginx.conf.template"
    if os.path.exists(tpl_path):
        with open(tpl_path, "r") as f:
            tcontent = f.read()
        target_to = "proxy_read_timeout 300s;\n        proxy_send_timeout 300s;"
        repl_to = "proxy_read_timeout 3600s;\n        proxy_send_timeout 3600s;"
        if target_to in tcontent:
            with open(tpl_path, "w") as f:
                f.write(tcontent.replace(target_to, repl_to, 1))

if __name__ == "__main__":
    try:
        patch()
    except Exception as e:
        pass
