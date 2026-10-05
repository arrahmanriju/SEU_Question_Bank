"""
loader.py — Speeder loading animation shown while slow work (DB queries, uploads) runs.

Usage:
    from loader import loading

    with loading("Loading departments…"):
        departments = get_departments()
"""

from contextlib import contextmanager

import streamlit as st

# NOTE: no blank lines or indentation inside this HTML — Streamlit's markdown parser
# would treat them as the end of the HTML block / a code block.
_LOADER_HTML = """<style>
.qbl-wrap{position:relative;width:100%;height:150px;overflow:hidden;color:inherit}
.qbl-loader{position:absolute;top:58%;left:50%;margin-left:-65px;animation:qbl-speeder .4s linear infinite;z-index:2}
.qbl-loader>span{height:5px;width:35px;background:currentColor;position:absolute;top:-19px;left:60px;border-radius:2px 10px 1px 0}
.qbl-base span{position:absolute;width:0;height:0;border-top:6px solid transparent;border-right:100px solid currentColor;border-bottom:6px solid transparent}
.qbl-base span:before{content:"";height:22px;width:22px;border-radius:50%;background:currentColor;position:absolute;right:-110px;top:-16px}
.qbl-base span:after{content:"";position:absolute;width:0;height:0;border-top:0 solid transparent;border-right:55px solid currentColor;border-bottom:16px solid transparent;top:-16px;right:-98px}
.qbl-face{position:absolute;height:12px;width:20px;background:currentColor;border-radius:20px 20px 0 0;transform:rotate(-40deg);right:-125px;top:-15px}
.qbl-face:after{content:"";height:12px;width:12px;background:currentColor;right:4px;top:7px;position:absolute;transform:rotate(40deg);transform-origin:50% 50%;border-radius:0 0 0 2px}
.qbl-loader>span>span{width:30px;height:1px;background:currentColor;position:absolute;animation:qbl-fazer1 .2s linear infinite}
.qbl-loader>span>span:nth-child(2){top:3px;animation:qbl-fazer2 .4s linear infinite}
.qbl-loader>span>span:nth-child(3){top:1px;animation:qbl-fazer3 .4s linear infinite;animation-delay:-1s}
.qbl-loader>span>span:nth-child(4){top:4px;animation:qbl-fazer4 1s linear infinite;animation-delay:-1s}
@keyframes qbl-fazer1{0%{left:0}100%{left:-80px;opacity:0}}
@keyframes qbl-fazer2{0%{left:0}100%{left:-100px;opacity:0}}
@keyframes qbl-fazer3{0%{left:0}100%{left:-50px;opacity:0}}
@keyframes qbl-fazer4{0%{left:0}100%{left:-150px;opacity:0}}
@keyframes qbl-speeder{0%{transform:translate(2px,1px) rotate(0deg)}10%{transform:translate(-1px,-3px) rotate(-1deg)}20%{transform:translate(-2px,0) rotate(1deg)}30%{transform:translate(1px,2px) rotate(0deg)}40%{transform:translate(1px,-1px) rotate(1deg)}50%{transform:translate(-1px,3px) rotate(-1deg)}60%{transform:translate(-1px,1px) rotate(0deg)}70%{transform:translate(3px,1px) rotate(-1deg)}80%{transform:translate(-2px,-1px) rotate(1deg)}90%{transform:translate(2px,1px) rotate(0deg)}100%{transform:translate(1px,-2px) rotate(-1deg)}}
.qbl-longfazers{position:absolute;width:100%;height:100%;overflow:hidden;pointer-events:none}
.qbl-longfazers span{position:absolute;height:2px;width:20%;background:currentColor;opacity:.1}
.qbl-longfazers span:nth-child(1){top:20%;animation:qbl-lf .6s linear infinite;animation-delay:-5s}
.qbl-longfazers span:nth-child(2){top:40%;animation:qbl-lf .8s linear infinite;animation-delay:-1s}
.qbl-longfazers span:nth-child(3){top:60%;animation:qbl-lf3 .6s linear infinite}
.qbl-longfazers span:nth-child(4){top:80%;animation:qbl-lf3 .5s linear infinite;animation-delay:-3s}
@keyframes qbl-lf{0%{left:200%}100%{left:-200%;opacity:0}}
@keyframes qbl-lf3{0%{left:200%}100%{left:-100%;opacity:0}}
.qbl-msg{text-align:center;margin:0 0 .5rem;font-size:.8rem;letter-spacing:.12em;text-transform:uppercase;opacity:.6;animation:qbl-pulse 1.2s ease-in-out infinite}
@keyframes qbl-pulse{0%,100%{opacity:.35}50%{opacity:.8}}
@media (prefers-reduced-motion:reduce){.qbl-loader,.qbl-loader span,.qbl-longfazers span,.qbl-msg{animation:none!important}}
</style>
<div class="qbl-wrap"><div class="qbl-longfazers"><span></span><span></span><span></span><span></span></div><div class="qbl-loader"><span><span></span><span></span><span></span><span></span></span><div class="qbl-base"><span></span><div class="qbl-face"></div></div></div></div>
<p class="qbl-msg">__MESSAGE__</p>"""


@contextmanager
def loading(message: str = "Loading…"):
    """Show the speeder animation while the wrapped block runs, then remove it."""
    placeholder = st.empty()
    placeholder.markdown(_LOADER_HTML.replace("__MESSAGE__", message), unsafe_allow_html=True)
    try:
        yield
    finally:
        placeholder.empty()
