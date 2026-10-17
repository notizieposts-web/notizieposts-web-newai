"""Logo Radar AI: marchio (tessera con radar) + scritta. SVG inline, colori dai token del tema."""
MARK = '<svg class="logo-mark" viewBox="0 0 32 32" width="30" height="30" aria-hidden="true" focusable="false"><rect width="32" height="32" rx="9" fill="var(--violet)"/><path d="M16 16 L16 5.5 A10.5 10.5 0 0 1 25.1 10.75 Z" fill="var(--bg)" opacity=".28"/><g fill="none" stroke="var(--bg)" stroke-linecap="round"><circle cx="16" cy="16" r="10.5" stroke-width="2" opacity=".6"/><circle cx="16" cy="16" r="5.6" stroke-width="2" opacity=".85"/><path d="M16 16 L25.1 10.75" stroke-width="2.4"/></g><circle cx="16" cy="16" r="2.3" fill="var(--bg)"/><circle cx="22.6" cy="21.4" r="2.2" fill="var(--bg)"/></svg>'
WORD = '<span class="logo-word">Radar<span class="logo-ai">AI</span></span>'
LOGO = MARK + WORD
CSS = (
 ".nav .brand{gap:.55rem!important}"
 ".logo-mark{flex:none;display:block}"
 ".logo-word{font-family:var(--head,system-ui);font-weight:800;font-size:1.12rem;letter-spacing:-.02em;color:var(--ink);line-height:1}"
 ".logo-ai{margin-left:.18em;padding:.12em .32em;border-radius:.35em;background:var(--violet);color:var(--bg);font-size:.78em;letter-spacing:.02em;vertical-align:.08em}"
 ".nav .brand:hover .logo-word{color:var(--violet)}.nav .brand:hover .logo-ai{color:var(--bg)}"
)
FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='9' fill='%234B4BF5'/%3E%3Cpath d='M16 16 L16 5.5 A10.5 10.5 0 0 1 25.1 10.75 Z' fill='%23fff' opacity='.28'/%3E%3Cg fill='none' stroke='%23fff' stroke-linecap='round'%3E%3Ccircle cx='16' cy='16' r='10.5' stroke-width='2' opacity='.6'/%3E%3Ccircle cx='16' cy='16' r='5.6' stroke-width='2' opacity='.85'/%3E%3Cpath d='M16 16 L25.1 10.75' stroke-width='2.4'/%3E%3C/g%3E%3Ccircle cx='16' cy='16' r='2.3' fill='%23fff'/%3E%3Ccircle cx='22.6' cy='21.4' r='2.2' fill='%23fff'/%3E%3C/svg%3E"
