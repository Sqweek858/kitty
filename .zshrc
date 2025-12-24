##### 1) 🎬 Cinematic intro (doar prima dată, înainte de tmux)
if [[ -z "$TMUX" && $- == i && -z "$_CYBER_INTRO_DONE" ]]; then
  export _CYBER_INTRO_DONE=1
  # Intro-ul va rula în shell-ul principal înainte de tmux
fi

##### 2) 🔁 Auto-start tmux (înainte de orice alt plugin/init)
if [[ -z "$TMUX" && $- == *i* && -t 1 ]]; then
  exec tmux new-session -A -s main
fi


ZINIT_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}/zinit/zinit.git"
if [[ ! -d "$ZINIT_HOME" ]]; then
    mkdir -p "$(dirname $ZINIT_HOME)"
    git clone https://github.com/zdharma-continuum/zinit.git "$ZINIT_HOME"
fi
source "${ZINIT_HOME}/zinit.zsh"

autoload -Uz _zinit
(( ${+_comps} )) && _comps[zinit]=_zinit

HISTFILE=~/.zsh_history
HISTSIZE=100000
SAVEHIST=100000
setopt EXTENDED_HISTORY
setopt HIST_EXPIRE_DUPS_FIRST
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_ALL_DUPS
setopt HIST_IGNORE_SPACE
setopt HIST_FIND_NO_DUPS
setopt HIST_SAVE_NO_DUPS
setopt HIST_VERIFY
setopt SHARE_HISTORY
setopt INC_APPEND_HISTORY
setopt HIST_REDUCE_BLANKS

setopt AUTO_CD
setopt AUTO_PUSHD
setopt PUSHD_IGNORE_DUPS
setopt PUSHDMINUS
setopt CDABLE_VARS
setopt MULTIOS
setopt EXTENDED_GLOB
setopt NO_BEEP
setopt INTERACTIVE_COMMENTS
setopt CORRECT
# setopt CORRECT_ALL
setopt AUTO_LIST
setopt AUTO_MENU
setopt ALWAYS_TO_END
setopt COMPLETE_IN_WORD
# setopt FLOW_CONTROL
setopt PATH_DIRS
setopt AUTO_NAME_DIRS
setopt AUTO_REMOVE_SLASH
setopt GLOB_COMPLETE
setopt GLOB_DOTS
setopt RC_QUOTES
setopt LONG_LIST_JOBS
setopt NOTIFY
setopt CHECK_JOBS
setopt HUP
setopt MAIL_WARNING
setopt PRINT_EXIT_VALUE
setopt COMBINING_CHARS
setopt EMACS
setopt NO_NOMATCH



if [[ -o interactive ]]; then
    # Core completions - BEFORE compinit
    zinit ice lucid blockf atpull"zinit creinstall -q ."
    zinit light zsh-users/zsh-completions

    # Intelligent completion
    # zinit ice lucid
    # zinit light marlonrichert/zsh-autocomplete

    # FZF-Tab
    zinit ice lucid
    zinit light Aloxaf/fzf-tab

    # History substring search
    zinit ice lucid
    zinit light zsh-users/zsh-history-substring-search
fi

# =========================
# ZINIT ANNEXES (FIX)
# =========================
# (broken)
# zinit light-mode for \
#     zdharma-continuum/zinit-annex-as-monitor \
#     zdharma-continuum/zinit-annex-bin-gem-node \
#     zdharma-continuum/zinit-annex-patch-dl \
#     zdharma-continuum/zinit-annex-rust

# (fixed)
zinit light zdharma-continuum/zinit-annex-as-monitor
zinit light zdharma-continuum/zinit-annex-bin-gem-node
zinit light zdharma-continuum/zinit-annex-patch-dl
zinit light zdharma-continuum/zinit-annex-rust


# =========================
# AUTOSUGGEST + COMPLETIONS (FIX)
# =========================
# (broken – ice fără plugin după, pentru că repo-ul e comentat)
# zinit wait lucid light-mode for \
#     atinit"zicompinit; zicdreplay" \
#         #zdharma-continuum/fast-syntax-highlighting \
#     atload"_zsh_autosuggest_start" \
#         zsh-users/zsh-autosuggestions \
#     blockf atpull'zinit creinstall -q .' \
#         zsh-users/zsh-completions

# (fixed) – atașez ice-urile de UN plugin real, nu de o linie comentată
# Dacă vrei fast-syntax-highlighting, îl pun aici corect:
zinit wait lucid for \
    atinit"zicompinit; zicdreplay" \
        zdharma-continuum/fast-syntax-highlighting \
    atload"_zsh_autosuggest_start" \
        zsh-users/zsh-autosuggestions \
    blockf atpull"zinit creinstall -q ." \
        zsh-users/zsh-completions


# =========================
# COMPINIT BLOCK (FIX – LIPSEA fi)
# =========================
autoload -Uz compinit
# rebuild compdump dacă e mai vechi de 24h (mh+24), altfel folosește cache
if [[ -n ${ZDOTDIR:-$HOME}/.zcompdump(#qN.mh+24) ]]; then
    compinit
else
    compinit -C
fi

# OMZ libraries
zinit wait lucid for \
    OMZL::clipboard.zsh \
    OMZL::compfix.zsh \
    OMZL::completion.zsh \
    OMZL::correction.zsh \
    OMZL::directories.zsh \
    OMZL::functions.zsh \
    OMZL::git.zsh \
    OMZL::grep.zsh \
    OMZL::history.zsh \
    OMZL::key-bindings.zsh \
    OMZL::misc.zsh \
    OMZL::spectrum.zsh \
    OMZL::termsupport.zsh \
    OMZL::theme-and-appearance.zsh

# OMZ plugins
zinit wait lucid for \
    OMZP::git \
    OMZP::sudo \
    OMZP::archlinux \
    OMZP::systemd \
    OMZP::command-not-found \
    OMZP::common-aliases \
    OMZP::compleat \
    OMZP::dirhistory \
    OMZP::jsontools \
    OMZP::colored-man-pages \
    OMZP::colorize \
    OMZP::cp \
    OMZP::extract \
    OMZP::fancy-ctrl-z \
    OMZP::history \
    OMZP::safe-paste \
    OMZP::transfer \
    OMZP::urltools \
    OMZP::web-search \
    OMZP::copybuffer \
    OMZP::copyfile \
    OMZP::copypath \
    OMZP::direnv \
    OMZP::encode64 \
    OMZP::rsync

# Additional plugins
zinit wait lucid for \
    hlissner/zsh-autopair \
    Tarrasch/zsh-bd \
    peterhurford/up.zsh \
    rupa/z \
    changyuheng/fz \
    andrewferrier/fzf-z \
    wfxr/forgit \
    laggardkernel/zsh-thefuck \
    djui/alias-tips \
    unixorn/autoupdate-antigen.zshplugin \
    TamCore/autoupdate-oh-my-zsh-plugins \
    desyncr/auto-ls \
    zdharma-continuum/history-search-multi-word

# Powerlevel10k
#zinit ice depth=1
#zinit light romkatv/powerlevel10k





# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
# SECTION 7: AUTOSUGGESTIONS CONFIGURATION
# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550

typeset -gA FAST_HIGHLIGHT_STYLES
FAST_HIGHLIGHT_STYLES[default]='fg=252'
FAST_HIGHLIGHT_STYLES[unknown-token]='fg=196,bold'
FAST_HIGHLIGHT_STYLES[reserved-word]='fg=197,bold'
FAST_HIGHLIGHT_STYLES[subcommand]='fg=39,bold'
FAST_HIGHLIGHT_STYLES[alias]='fg=45,bold'
FAST_HIGHLIGHT_STYLES[suffix-alias]='fg=45,bold'
FAST_HIGHLIGHT_STYLES[global-alias]='fg=45,bold'
FAST_HIGHLIGHT_STYLES[builtin]='fg=51,bold'
FAST_HIGHLIGHT_STYLES[function]='fg=39,bold'
FAST_HIGHLIGHT_STYLES[command]='fg=51,bold'
FAST_HIGHLIGHT_STYLES[precommand]='fg=197,bold'
FAST_HIGHLIGHT_STYLES[commandseparator]='fg=213,bold'
FAST_HIGHLIGHT_STYLES[hashed-command]='fg=51,bold'
FAST_HIGHLIGHT_STYLES[autodirectory]='fg=48,bold,underline'
FAST_HIGHLIGHT_STYLES[path]='fg=48,underline'
FAST_HIGHLIGHT_STYLES[path_pathseparator]='fg=198,bold,underline'
FAST_HIGHLIGHT_STYLES[path_prefix]='fg=48,underline'
FAST_HIGHLIGHT_STYLES[path_prefix_pathseparator]='fg=198,bold,underline'
FAST_HIGHLIGHT_STYLES[globbing]='fg=226,bold'
FAST_HIGHLIGHT_STYLES[globbing-ext]='fg=214,bold'
FAST_HIGHLIGHT_STYLES[history-expansion]='fg=39,bold'
FAST_HIGHLIGHT_STYLES[single-hyphen-option]='fg=228'
FAST_HIGHLIGHT_STYLES[double-hyphen-option]='fg=228,bold'
FAST_HIGHLIGHT_STYLES[back-quoted-argument]='fg=214'
FAST_HIGHLIGHT_STYLES[back-quoted-argument-unclosed]='fg=196,bold'
FAST_HIGHLIGHT_STYLES[single-quoted-argument]='fg=48'
FAST_HIGHLIGHT_STYLES[single-quoted-argument-unclosed]='fg=196,bold'
FAST_HIGHLIGHT_STYLES[double-quoted-argument]='fg=48'
FAST_HIGHLIGHT_STYLES[double-quoted-argument-unclosed]='fg=196,bold'
FAST_HIGHLIGHT_STYLES[dollar-quoted-argument]='fg=48'
FAST_HIGHLIGHT_STYLES[dollar-quoted-argument-unclosed]='fg=196,bold'
FAST_HIGHLIGHT_STYLES[rc-quote]='fg=45'
FAST_HIGHLIGHT_STYLES[dollar-double-quoted-argument]='fg=45'
FAST_HIGHLIGHT_STYLES[back-double-quoted-argument]='fg=45'
FAST_HIGHLIGHT_STYLES[back-dollar-quoted-argument]='fg=45'
FAST_HIGHLIGHT_STYLES[assign]='fg=213,bold'
FAST_HIGHLIGHT_STYLES[redirection]='fg=213,bold'
FAST_HIGHLIGHT_STYLES[comment]='fg=240,italic'
FAST_HIGHLIGHT_STYLES[named-fd]='fg=45'
FAST_HIGHLIGHT_STYLES[numeric-fd]='fg=45'
FAST_HIGHLIGHT_STYLES[arg0]='fg=51,bold'
FAST_HIGHLIGHT_STYLES[here-string-tri]='fg=48'
FAST_HIGHLIGHT_STYLES[here-string-word]='fg=48'
FAST_HIGHLIGHT_STYLES[secondary]='fg=248,italic'
FAST_HIGHLIGHT_STYLES[case-input]='fg=45'
FAST_HIGHLIGHT_STYLES[case-parentheses]='fg=213,bold'
FAST_HIGHLIGHT_STYLES[case-condition]='fg=51,bold'
FAST_HIGHLIGHT_STYLES[paired-bracket]='fg=226,bold'
FAST_HIGHLIGHT_STYLES[bracket-level-1]='fg=51,bold'
FAST_HIGHLIGHT_STYLES[bracket-level-2]='fg=213,bold'
FAST_HIGHLIGHT_STYLES[bracket-level-3]='fg=45,bold'
FAST_HIGHLIGHT_STYLES[variable]='fg=45'
FAST_HIGHLIGHT_STYLES[correct-subtle]='fg=48'
FAST_HIGHLIGHT_STYLES[incorrect-subtle]='fg=196'
FAST_HIGHLIGHT_STYLES[subtle-separator]='fg=248'
FAST_HIGHLIGHT_STYLES[subtle-bg]='bg=234'

# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
# SECTION 8: COMPLETION SYSTEM CONFIGURATION
# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550

zstyle ':completion:*' completer _extensions _complete
zstyle ':completion:*' use-cache on
zstyle ':completion:*' cache-path "${XDG_CACHE_HOME:-$HOME/.cache}/zsh/.zcompcache"
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'
zstyle ':completion:*' special-dirs true
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*' squeeze-slashes true
zstyle ':completion:*' complete-options true
zstyle ':completion:::::corrections' format '%F{226}── %d (errors: %e) ──%f'
zstyle ':completion:::::messages'   format '%F{213}── %d ──%f'
zstyle ':completion:::::warnings'   format '%F{196}── no matches found ──%f'
zstyle ':completion:*:*:*:*:default' list-colors ${(s.:.)LS_COLORS}
zstyle ':completion:*:*:kill:*:processes' list-colors '=(#b) #([0-9]#) ([0-9a-z-]#)*=01;34=0=01'
zstyle ':completion:*:*:*:*:processes' command 'ps -u $USER -o pid,user,comm -w -w'
zstyle ':completion:*:cd:*' tag-order local-directories directory-stack path-directories
zstyle ':completion:*' group-name ''
zstyle ':completion:*:manuals' separate-sections true
zstyle ':completion:*:manuals.(^1*)' insert-sections true
zstyle ':completion:*:functions' ignored-patterns '(_*|pre(cmd|exec))'
zstyle ':completion:*:*:-subscript-:*' tag-order indexes parameters
zstyle ':completion:*:*:cd:*:directory-stack' menu yes select
zstyle ':completion:*:-tilde-:*' group-order 'named-directories' 'path-directories' 'users' 'expand'
zstyle ':completion:*:history-words' stop yes
zstyle ':completion:*:history-words' remove-all-dups yes
zstyle ':completion:*:history-words' list false
zstyle ':completion:*:history-words' menu yes
zstyle ':completion:*:ssh:*' tag-order 'hosts:-host:host hosts:-domain:domain hosts:-ipaddr:ip\ address *'
zstyle ':completion:*:ssh:*' group-order users hosts-domain hosts-host users hosts-ipaddr
zstyle ':completion:*:(ssh|scp|rsync):*:hosts-host' ignored-patterns '*(.|:)*' loopback ip6-loopback localhost ip6-localhost broadcasthost
zstyle ':completion:*:(ssh|scp|rsync):*:hosts-domain' ignored-patterns '<->.<->.<->.<->' '^[-[:alnum:]]##.[-[:alnum:]]##*'
zstyle ':completion:*:(ssh|scp|rsync):*:hosts-ipaddr' ignored-patterns '^(<->.<->.<->.<->|(|-)-)' '127.0.0.<->' '255.255.255.255' '::1' 'fe80::*'
zstyle ':completion:*' rehash true
zstyle ':completion:*' accept-exact '*(N)'
zstyle ':completion:*' file-sort modification
zstyle ':completion:*:complete:-command-::commands' ignored-patterns '*\~'

# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
# SECTION 9: FZF CONFIGURATION
# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550

zstyle ':fzf-tab:*' fzf-command ftb-tmux-popup
zstyle ':fzf-tab:*' fzf-flags --border=rounded --height=60% --layout=reverse --info=inline
zstyle ':fzf-tab:*' fzf-pad 4
zstyle ':fzf-tab:*' fzf-min-height 20
zstyle ':fzf-tab:*' switch-group ',' '.'
zstyle ':fzf-tab:*' continuous-trigger '/'
zstyle ':fzf-tab:*' accept-line enter
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'eza -1 --color=always --icons $realpath'
zstyle ':fzf-tab:complete:*:*' fzf-preview 'less ${(Q)realpath}'
zstyle ':fzf-tab:complete:*:options' fzf-preview ''
zstyle ':fzf-tab:complete:*:argument-1' fzf-preview ''

export FZF_DEFAULT_OPTS="
--color=fg:#00ffff,bg:#0a0a12,hl:#ff00ff
--color=fg+:#7df9ff,bg+:#1a1a2e,hl+:#00ffff
--color=info:#ffff00,prompt:#00ffff,pointer:#ff00ff
--color=marker:#00ff9f,spinner:#ff00ff,header:#00ff9f
--color=gutter:#0a0a12,border:#00ffff
--border=rounded
--height=60%
--layout=reverse
--info=inline
--prompt='❯'
--pointer='▶'
--marker='✓'
--bind='ctrl-a:select-all'
--bind='ctrl-d:deselect-all'
--bind='ctrl-t:toggle-all'
--bind='ctrl-y:execute-silent(echo {+} | xclip -selection clipboard)'
--bind='ctrl-e:execute(echo {+} | xargs -o nvim)'
--bind='ctrl-v:execute(code {+})'
--bind='?:toggle-preview'
--bind='ctrl-f:preview-page-down'
--bind='ctrl-b:preview-page-up'
"

export FZF_CTRL_R_OPTS="
--preview='echo {}' --preview-window down:3:wrap
--bind='ctrl-y:execute-silent(echo -n {2..} | xclip -selection clipboard)+abort'
"

export FZF_ALT_C_OPTS="
--preview='eza --tree --icons --level=2 --color=always {}'
"

export FZF_CTRL_T_OPTS="
--preview='bat --style=numbers --color=always --line-range :500 {} 2>/dev/null || cat {}'
"

typeset -gA CYBER_COLORS
CYBER_COLORS=(
    [cyan]='\033[38;2;0;255;255m'
    [magenta]='\033[38;2;255;0;255m'
    [green]='\033[38;2;0;255;127m'
    [yellow]='\033[38;2;255;255;0m'
    [red]='\033[38;2;255;0;85m'
    [blue]='\033[38;2;0;170;255m'
    [orange]='\033[38;2;255;136;0m'
    [purple]='\033[38;2;170;85;255m'
    [pink]='\033[38;2;255;85;170m'
    [white]='\033[38;2;125;249;255m'
    [gray]='\033[38;2;128;128;128m'
    [dark]='\033[38;2;40;40;50m'
    [neon_cyan]='\033[38;2;0;255;255m'
    [neon_magenta]='\033[38;2;255;0;170m'
    [neon_green]='\033[38;2;57;255;20m'
    [neon_yellow]='\033[38;2;255;255;0m'
    [neon_red]='\033[38;2;255;0;68m'
    [neon_blue]='\033[38;2;0;191;255m'
    [electric_blue]='\033[38;2;125;249;255m'
    [hot_pink]='\033[38;2;255;20;147m'
    [acid_green]='\033[38;2;176;255;0m'
    [sunset_orange]='\033[38;2;255;99;71m'
    [deep_purple]='\033[38;2;148;0;211m'
    [gold]='\033[38;2;255;215;0m'
)

# Background colors
typeset -gA CYBER_BG
CYBER_BG=(
    [dark]='\033[48;2;10;10;18m'
    [darker]='\033[48;2;5;5;10m'
    [panel]='\033[48;2;20;20;35m'
    [highlight]='\033[48;2;40;40;60m'
    [success]='\033[48;2;0;50;30m'
    [warning]='\033[48;2;50;40;0m'
    [error]='\033[48;2;50;0;20m'
)

# Text styles
typeset -gA CYBER_STYLE
CYBER_STYLE=(
    [reset]='\033[0m'
    [bold]='\033[1m'
    [dim]='\033[2m'
    [italic]='\033[3m'
    [underline]='\033[4m'
    [blink]='\033[5m'
    [reverse]='\033[7m'
    [hidden]='\033[8m'
    [strike]='\033[9m'
)

# Legacy compatibility
CYBERPUNK_CYAN='\033[38;5;51m'
CYBERPUNK_MAGENTA='\033[38;5;201m'
CYBERPUNK_GREEN='\033[38;5;46m'
CYBERPUNK_YELLOW='\033[38;5;226m'
CYBERPUNK_RED='\033[38;5;196m'
CYBERPUNK_BLUE='\033[38;5;39m'
CYBERPUNK_ORANGE='\033[38;5;208m'
CYBERPUNK_PURPLE='\033[38;5;141m'
CYBERPUNK_PINK='\033[38;5;213m'
CYBERPUNK_WHITE='\033[38;5;255m'
CYBERPUNK_GRAY='\033[38;5;245m'
CYBERPUNK_DARK='\033[38;5;236m'
RESET='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'
ITALIC='\033[3m'
UNDERLINE='\033[4m'
BLINK='\033[5m'
REVERSE='\033[7m'
HIDDEN='\033[8m'
STRIKETHROUGH='\033[9m'

export LS_COLORS="di=1;38;5;51:ln=38;5;213;4:so=38;5;197:pi=38;5;214:ex=1;38;5;46:bd=38;5;214;1:cd=38;5;214:su=38;5;196;1:sg=38;5;196:tw=38;5;51:ow=38;5;51:st=38;5;86:mi=38;5;196;9:or=38;5;196;9:*.tar=38;5;197:*.tgz=38;5;197:*.arc=38;5;197:*.arj=38;5;197:*.taz=38;5;197:*.lha=38;5;197:*.lz4=38;5;197:*.lzh=38;5;197:*.lzma=38;5;197:*.tlz=38;5;197:*.txz=38;5;197:*.tzo=38;5;197:*.t7z=38;5;197:*.zip=38;5;197:*.z=38;5;197:*.dz=38;5;197:*.gz=38;5;197:*.lrz=38;5;197:*.lz=38;5;197:*.lzo=38;5;197:*.xz=38;5;197:*.zst=38;5;197:*.tzst=38;5;197:*.bz2=38;5;197:*.bz=38;5;197:*.tbz=38;5;197:*.tbz2=38;5;197:*.tz=38;5;197:*.deb=38;5;197:*.rpm=38;5;197:*.jar=38;5;197:*.war=38;5;197:*.ear=38;5;197:*.sar=38;5;197:*.rar=38;5;197:*.alz=38;5;197:*.ace=38;5;197:*.zoo=38;5;197:*.cpio=38;5;197:*.7z=38;5;197:*.rz=38;5;197:*.cab=38;5;197:*.wim=38;5;197:*.swm=38;5;197:*.dwm=38;5;197:*.esd=38;5;197:*.jpg=38;5;213:*.jpeg=38;5;213:*.mjpg=38;5;213:*.mjpeg=38;5;213:*.gif=38;5;213:*.bmp=38;5;213:*.pbm=38;5;213:*.pgm=38;5;213:*.ppm=38;5;213:*.tga=38;5;213:*.xbm=38;5;213:*.xpm=38;5;213:*.tif=38;5;213:*.tiff=38;5;213:*.png=38;5;213:*.svg=38;5;213:*.svgz=38;5;213:*.mng=38;5;213:*.pcx=38;5;213:*.mov=38;5;213:*.mpg=38;5;213:*.mpeg=38;5;213:*.m2v=38;5;213:*.mkv=38;5;213:*.webm=38;5;213:*.webp=38;5;213:*.ogm=38;5;213:*.mp4=38;5;213:*.m4v=38;5;213:*.mp4v=38;5;213:*.vob=38;5;213:*.qt=38;5;213:*.nuv=38;5;213:*.wmv=38;5;213:*.asf=38;5;213:*.rm=38;5;213:*.rmvb=38;5;213:*.flc=38;5;213:*.avi=38;5;213:*.fli=38;5;213:*.flv=38;5;213:*.gl=38;5;213:*.dl=38;5;213:*.xcf=38;5;213:*.xwd=38;5;213:*.yuv=38;5;213:*.cgm=38;5;213:*.emf=38;5;213:*.ogv=38;5;213:*.ogx=38;5;213:*.aac=38;5;45:*.au=38;5;45:*.flac=38;5;45:*.m4a=38;5;45:*.mid=38;5;45:*.midi=38;5;45:*.mka=38;5;45:*.mp3=38;5;45:*.mpc=38;5;45:*.ogg=38;5;45:*.ra=38;5;45:*.wav=38;5;45:*.oga=38;5;45:*.opus=38;5;45:*.spx=38;5;45:*.xspf=38;5;45:*.pdf=38;5;196:*.doc=38;5;39:*.docx=38;5;39:*.xls=38;5;48:*.xlsx=38;5;48:*.ppt=38;5;214:*.pptx=38;5;214:*.odt=38;5;39:*.ods=38;5;48:*.odp=38;5;214:*.txt=38;5;252:*.md=38;5;252:*.markdown=38;5;252:*.rst=38;5;252:*.tex=38;5;252:*.nfo=38;5;252:*.log=38;5;240:*.bak=38;5;240:*.old=38;5;240:*.orig=38;5;240:*.swp=38;5;240:*.tmp=38;5;240:*.pid=38;5;240:*.cfg=38;5;228:*.conf=38;5;228:*.config=38;5;228:*.ini=38;5;228:*.json=38;5;228:*.yaml=38;5;228:*.yml=38;5;228:*.toml=38;5;228:*.xml=38;5;228:*.c=38;5;51:*.cpp=38;5;51:*.cc=38;5;51:*.cxx=38;5;51:*.h=38;5;51:*.hpp=38;5;51:*.hh=38;5;51:*.hxx=38;5;51:*.go=38;5;51:*.rs=38;5;208:*.py=38;5;226:*.pyc=38;5;240:*.pyo=38;5;240:*.pyd=38;5;240:*.rb=38;5;197:*.js=38;5;228:*.jsx=38;5;228:*.ts=38;5;39:*.tsx=38;5;39:*.vue=38;5;48:*.php=38;5;141:*.lua=38;5;39:*.java=38;5;208:*.class=38;5;240:*.jar=38;5;197:*.kt=38;5;141:*.kts=38;5;141:*.scala=38;5;197:*.cs=38;5;141:*.fs=38;5;39:*.fsx=38;5;39:*.hs=38;5;141:*.lhs=38;5;141:*.ml=38;5;208:*.mli=38;5;208:*.elm=38;5;39:*.erl=38;5;197:*.hrl=38;5;197:*.ex=38;5;141:*.exs=38;5;141:*.clj=38;5;48:*.cljs=38;5;48:*.cljc=38;5;48:*.edn=38;5;48:*.dart=38;5;39:*.swift=38;5;208:*.r=38;5;39:*.R=38;5;39:*.sql=38;5;39:*.sh=38;5;48:*.bash=38;5;48:*.zsh=38;5;48:*.fish=38;5;48:*.ps1=38;5;39:*.psm1=38;5;39:*.bat=38;5;48:*.cmd=38;5;48:*.awk=38;5;48:*.sed=38;5;48:*.pl=38;5;39:*.pm=38;5;39:*.t=38;5;39:*.html=38;5;208:*.htm=38;5;208:*.xhtml=38;5;208:*.css=38;5;39:*.scss=38;5;213:*.sass=38;5;213:*.less=38;5;39:*.styl=38;5;39:*.coffee=38;5;214:*.ejs=38;5;208:*.erb=38;5;197:*.haml=38;5;252:*.slim=38;5;252:*.pug=38;5;252:*.jade=38;5;252:*.mustache=38;5;214:*.hbs=38;5;214:*.handlebars=38;5;214:*.twig=38;5;48:*.blade.php=38;5;197:*.Makefile=38;5;228:*.makefile=38;5;228:*.mk=38;5;228:*.cmake=38;5;228:*.ninja=38;5;228:*.dockerfile=38;5;39:*.Dockerfile=38;5;39:*.vagrantfile=38;5;39:*.Vagrantfile=38;5;39:*.tf=38;5;141:*.tfvars=38;5;141:*.tfstate=38;5;240:*.hcl=38;5;141:*.nix=38;5;39:*.dhall=38;5;39:*.pp=38;5;214:*.epp=38;5;214:*.sls=38;5;39:*.jinja=38;5;197:*.jinja2=38;5;197:*.j2=38;5;197:*.graphql=38;5;213:*.gql=38;5;213:*.proto=38;5;39:*.thrift=38;5;48:*.avsc=38;5;228:*.avdl=38;5;228:*Gemfile=38;5;197:*Rakefile=38;5;197:*Guardfile=38;5;197:*Podfile=38;5;197:*Fastfile=38;5;197:*Brewfile=38;5;197:*package.json=38;5;228:*package-lock.json=38;5;240:*yarn.lock=38;5;240:*Cargo.toml=38;5;208:*Cargo.lock=38;5;240:*go.mod=38;5;51:*go.sum=38;5;240:*requirements.txt=38;5;226:*Pipfile=38;5;226:*Pipfile.lock=38;5;240:*pyproject.toml=38;5;226:*poetry.lock=38;5;240:*setup.py=38;5;226:*setup.cfg=38;5;228:*tox.ini=38;5;228:*composer.json=38;5;141:*composer.lock=38;5;240:*mix.exs=38;5;141:*mix.lock=38;5;240:*pom.xml=38;5;208:*build.gradle=38;5;48:*build.gradle.kts=38;5;48:*settings.gradle=38;5;48:*settings.gradle.kts=38;5;48:*build.sbt=38;5;197:*.sbt=38;5;197:*project.clj=38;5;48:*deps.edn=38;5;48:*shadow-cljs.edn=38;5;48:*stack.yaml=38;5;141:*cabal.project=38;5;141:*.cabal=38;5;141:*dune=38;5;208:*dune-project=38;5;208:*elm.json=38;5;39:*rebar.config=38;5;197:*.gitignore=38;5;240:*.gitattributes=38;5;240:*.gitmodules=38;5;240:*.gitconfig=38;5;240:*.git=38;5;240:*.hgignore=38;5;240:*.hg=38;5;240:*.svn=38;5;240:*.npmignore=38;5;240:*.npmrc=38;5;240:*.nvmrc=38;5;240:*.node-version=38;5;240:*.ruby-version=38;5;240:*.python-version=38;5;240:*.java-version=38;5;240:*.tool-versions=38;5;240:*.env=38;5;228:*.env.local=38;5;228:*.env.development=38;5;228:*.env.production=38;5;228:*.env.test=38;5;228:*.env.example=38;5;240:*.editorconfig=38;5;240:*.prettierrc=38;5;240:*.prettierignore=38;5;240:*.eslintrc=38;5;240:*.eslintignore=38;5;240:*.stylelintrc=38;5;240:*tsconfig.json=38;5;39:*jsconfig.json=38;5;228:*webpack.config.js=38;5;228:*rollup.config.js=38;5;228:*vite.config.js=38;5;228:*vite.config.ts=38;5;39:*babel.config.js=38;5;228:*.babelrc=38;5;228:*jest.config.js=38;5;197:*vitest.config.js=38;5;228:*vitest.config.ts=38;5;39:*karma.conf.js=38;5;228:*protractor.conf.js=38;5;228:*cypress.json=38;5;48:*playwright.config.js=38;5;48:*playwright.config.ts=38;5;39:*.dockerignore=38;5;39:*docker-compose.yml=38;5;39:*docker-compose.yaml=38;5;39:*docker-compose.override.yml=38;5;39:*.travis.yml=38;5;228:*.gitlab-ci.yml=38;5;214:*Jenkinsfile=38;5;39:*.circleci=38;5;48:*.github=38;5;252:*CODEOWNERS=38;5;228:*LICENSE=38;5;252:*LICENSE.md=38;5;252:*LICENSE.txt=38;5;252:*COPYING=38;5;252:*README=38;5;226:*README.md=38;5;226:*README.txt=38;5;226:*README.rst=38;5;226:*CHANGELOG=38;5;252:*CHANGELOG.md=38;5;252:*HISTORY=38;5;252:*HISTORY.md=38;5;252:*CONTRIBUTING=38;5;252:*CONTRIBUTING.md=38;5;252:*AUTHORS=38;5;252:*AUTHORS.md=38;5;252:*TODO=38;5;226:*TODO.md=38;5;226:*THANKS=38;5;252:*THANKS.md=38;5;252:*VERSION=38;5;252:*MANIFEST=38;5;252"

export EZA_COLORS="di=1;38;5;51:ln=38;5;213;4:so=38;5;197:pi=38;5;214:ex=1;38;5;46:bd=38;5;214;1:cd=38;5;214:su=38;5;196;1:sg=38;5;196:tw=38;5;51:ow=38;5;51:st=38;5;86:ur=38;5;228:uw=38;5;197:ux=38;5;46:ue=38;5;46:gr=38;5;228:gw=38;5;197:gx=38;5;46:tr=38;5;228:tw=38;5;197:tx=38;5;46:sn=38;5;46:sb=38;5;46:df=38;5;46:ds=38;5;197:uu=38;5;228:un=38;5;197:gu=38;5;228:gn=38;5;197:da=38;5;39:ga=38;5;46:gm=38;5;228:gd=38;5;197:gv=38;5;51:gt=38;5;213:xx=38;5;240"


# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
# SECTION 10: GLOBAL STATE MANAGEMENT
# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550



# Directories for storing data
typeset -g CYBER_DATA_DIR="${HOME}/.local/share/cyber-shell"
typeset -g CYBER_CACHE_DIR="${HOME}/.cache/cyber-shell"
typeset -g CYBER_CONFIG_DIR="${HOME}/.config/cyber-shell"

# Create directories if they don't exist
mkdir -p "$CYBER_DATA_DIR"/{history,macros,profiles,heatmaps,timelines,clipboard}
mkdir -p "$CYBER_CACHE_DIR"/{predictions,nlp,search}
mkdir -p "$CYBER_CONFIG_DIR"

# Global state variables
typeset -g CYBER_LAST_EXIT_CODE=0
typeset -g CYBER_LAST_COMMAND=""
typeset -g CYBER_LAST_COMMAND_TIME=0
typeset -g CYBER_IS_SUDO=0
typeset -g CYBER_IS_DANGEROUS=0
typeset -g CYBER_TERMINAL_BUSY=0
typeset -g CYBER_AMBIENT_MODE=0
typeset -g CYBER_LAST_ACTIVITY=$(date +%s)
typeset -g CYBER_CPU_LOAD=0
typeset -g CYBER_BATTERY_LEVEL=100
typeset -g CYBER_BATTERY_CHARGING=0

# Clipboard ring
typeset -ga CYBER_CLIPBOARD_RING=()
typeset -g CYBER_CLIPBOARD_MAX=10

# Command history tracking for predictions
typeset -ga CYBER_COMMAND_SEQUENCE=()
typeset -g CYBER_COMMAND_SEQUENCE_MAX=100

# Macro recording state
typeset -g CYBER_RECORDING_MACRO=0
typeset -g CYBER_CURRENT_MACRO=""
typeset -ga CYBER_MACRO_COMMANDS=()

# Timeline state
typeset -ga CYBER_TIMELINE=()
typeset -g CYBER_TIMELINE_MAX=500
# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
# SECTION 11: UTILITY FUNCTIONS - CORE
# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550

# Print with cyberpunk styling
cyber_print() {
    local color="${1:-cyan}"
    local message="$2"
    local style="${3:-}"

    local color_code="${CYBER_COLORS[$color]:-${CYBER_COLORS[cyan]}}"
    local style_code="${CYBER_STYLE[$style]:-}"

    printf "%b%b%s%b\n" "$color_code" "$style_code" "$message" "${CYBER_STYLE[reset]}"
}

# Box drawing utilities
cyber_box_top() {
  local width=${1:-60}
  local color="${2:-cyan}"
  print -n -- "${CYBER_COLORS[$color]}╔"
  repeat $width print -n -- "═"
  print -- "╗${CYBER_STYLE[reset]}"
}

cyber_box_bottom() {
  local width=${1:-60}
  local color="${2:-cyan}"
  print -n -- "${CYBER_COLORS[$color]}╚"
  repeat $width print -n -- "═"
  print -- "╝${CYBER_STYLE[reset]}"
}

cyber_box_line() {
  local content="$1"
  local width=${2:-60}
  local color="${3:-cyan}"

  local content_len=${#content}
  local padding=$((width - content_len))
  (( padding < 0 )) && padding=0

  print -n -- "${CYBER_COLORS[$color]}║${CYBER_STYLE[reset]} "
  print -n -- "$content"
  (( padding > 0 )) && printf "%*s" "$padding" ""
  print -- " ${CYBER_COLORS[$color]}║${CYBER_STYLE[reset]}"
}

cyber_box_separator() {
  local width=${1:-60}
  local color="${2:-cyan}"
  print -n -- "${CYBER_COLORS[$color]}╠"
  repeat $width print -n -- "═"
  print -- "╣${CYBER_STYLE[reset]}"
}

# Get system metrics
get_cpu_load() {
    local load=$(cat /proc/loadavg 2>/dev/null | cut -d' ' -f1)
    CYBER_CPU_LOAD="${load:-0}"
    echo "$CYBER_CPU_LOAD"
}

get_battery_info() {
    local bat_path="/sys/class/power_supply/BAT0"
    if [[ -d "$bat_path" ]]; then
        CYBER_BATTERY_LEVEL=$(cat "$bat_path/capacity" 2>/dev/null || echo 100)
        local status=$(cat "$bat_path/status" 2>/dev/null)
        [[ "$status" == "Charging" ]] && CYBER_BATTERY_CHARGING=1 || CYBER_BATTERY_CHARGING=0
    else
        CYBER_BATTERY_LEVEL=100
        CYBER_BATTERY_CHARGING=0
    fi
}
autoload -Uz add-zsh-hook

typeset -g CYBER_STDERR_LOG="${XDG_CACHE_HOME:-$HOME/.cache}/cyberpunk_stderr.log"
typeset -gi CYBER_STDERR_FD=-1

typeset -gi CYBER_TOPBAR_ENABLED=${CYBER_TOPBAR_ENABLED:-1}
typeset -gi CYBER_DOCTOR_AUTO=${CYBER_DOCTOR_AUTO:-0}

cyber_topbar_apply_scroll_region() {
  [[ -t 1 ]] || return
  # Nu mai manipulăm scroll region - cauzează probleme
  return 0
}

cyber_topbar_reset_scroll_region() {
  [[ -t 1 ]] || return
  # printf '\e[r'              # reset full scroll region
}
cyber_enable_mouse()  { [[ -t 1 ]] || return; printf '\e[?1000h\e[?1006h'; }
cyber_disable_mouse() { [[ -t 1 ]] || return; printf '\e[?1000l\e[?1006l'; }

cyber_clear_utility_bar() {
  [[ -t 1 ]] || return
  printf '\e[s\e[%d;1H\e[2K\e[u' "${LINES:-24}"
}

cyber_parallax_badge() {
  # parallax minimal: un “star” care se mută la fiecare comandă
  local chars=('·' '∙' '•' '✦')
  local n=${#chars[@]}
  local idx=$(( (PARALLAX_BG_OFFSET % n) + 1 ))
  print -n -- "${chars[$idx]}"
}
cyber_draw_parallax_header() {
  [[ -t 1 ]] || return
  (( PARALLAX_ENABLED )) || return
  printf '\e[s'
  generate_parallax_bg 0
  printf '\e[u'
}

cyber_draw_utility_bar() {
  [[ -t 1 ]] || return
  (( CYBER_TOPBAR_ENABLED )) || { cyber_clear_utility_bar; return; }

  local cols=${COLUMNS:-80}
  (( cols < 50 )) && return

  local tstamp="$(date '+%H:%M:%S')"
  local load="$(get_cpu_load 2>/dev/null)"
  local bat="${CYBER_BATTERY_LEVEL:-100}%"

  local mem="n/a"
  if command -v free >/dev/null 2>&1; then
    local used total
    used=$(free -m | awk '/^Mem:/ {print $3}')
    total=$(free -m | awk '/^Mem:/ {print $2}')
    mem="${used:-0}M/${total:-0}M"
  fi

  local px=""
  if (( ${PARALLAX_ENABLED:-0} )); then
    px="PX:$(cyber_parallax_badge)"
  else
    px="PX:off"
  fi

  local doc=""
  if (( CYBER_DOCTOR_AUTO )); then
    doc="DOC:on"
  else
    doc="DOC:off"
  fi
#button thing
  typeset -gA CYBER_TOPBAR_BTN_RANGES
  typeset -gi CYBER_TOPBAR_START_COL=1
  CYBER_TOPBAR_BTN_RANGES=()

  local buttons="" info=""
  local pos=1

  _btn() {
    local id="$1" label="$2"
    local seg="[$label]"
    local start=$pos
    buttons+="$seg "
    pos=$((pos + ${#seg} + 1))
    local end=$((pos - 2))
    CYBER_TOPBAR_BTN_RANGES[$id]="${start}:${end}"
  }

  _btn S "Search"
  _btn C "Clip"
  _btn F "Files"
  _btn M "Macros"
  _btn T "Timeline"
  _btn H "Heat"
  _btn D "Doctor"
  _btn P "Parallax"
  _btn Q "Help"

  local proj=""
  [[ -n "$CURRENT_PROJECT_TYPE" ]] && proj="${CURRENT_PROJECT_TYPE}:${CURRENT_PROJECT}"

  local gitb=""
  if command -v git >/dev/null 2>&1; then
    gitb="$(git branch --show-current 2>/dev/null)"
    [[ -n "$gitb" ]] && gitb="git:${gitb}"
  fi

  local busy=$([[ ${CYBER_TERMINAL_BUSY:-0} -eq 1 ]] && echo "BUSY" || echo "IDLE")
  info="| $busy | ${proj} ${gitb} | CPU:${load:-0} RAM:${mem} BAT:${bat} ${tstamp}"

  local content="${buttons}${info}"


  # right align
  local len=${#content}
  if (( len > cols )); then
    content="${content[1,$cols]}"
    len=${#content}
  fi
  local col=$(( cols - len + 1 ))
  (( col < 1 )) && col=1
  CYBER_TOPBAR_START_COL=$col
# Desenează pe ULTIMUL rând, nu primul
  printf '\e[s\e[%d;1H\e[2K\e[%d;%dH' "$LINES" "$LINES" "$col"
  print -n -- "${CYBER_BG[panel]}${CYBER_COLORS[electric_blue]}${content}${CYBER_STYLE[reset]}"
  printf '\e[u'

}

cyber_toggle_topbar_widget() {
  (( CYBER_TOPBAR_ENABLED = !CYBER_TOPBAR_ENABLED ))
  if (( CYBER_TOPBAR_ENABLED )); then
    cyber_topbar_apply_scroll_region
    cyber_draw_utility_bar
    zle -M "Topbar: ON"
  else
    cyber_clear_utility_bar
    cyber_topbar_reset_scroll_region
    zle -M "Topbar: OFF"
  fi
}
zle -N cyber_toggle_topbar_widget
bindkey '^[u' cyber_toggle_topbar_widget

cyber_toggle_doctor_widget() {
  (( CYBER_DOCTOR_AUTO = !CYBER_DOCTOR_AUTO ))
  zle -M "Doctor: $([[ $CYBER_DOCTOR_AUTO -eq 1 ]] && echo ON || echo OFF)"
  cyber_draw_utility_bar
}
zle -N cyber_toggle_doctor_widget
bindkey '^[d' cyber_toggle_doctor_widget

cyber_toggle_parallax_widget() {
  (( PARALLAX_ENABLED = !PARALLAX_ENABLED ))
  zle -M "Parallax: $([[ $PARALLAX_ENABLED -eq 1 ]] && echo ON || echo OFF)"

  if (( PARALLAX_ENABLED )); then
    # dacă mai rulează animația de intro, oprește-o
    if [[ -n "${CYBER_GRADIENT_PID:-}" ]] && kill -0 "$CYBER_GRADIENT_PID" 2>/dev/null; then
      kill "$CYBER_GRADIENT_PID" 2>/dev/null
      CYBER_GRADIENT_PID=""
    fi
    parallax_start
  else
    parallax_stop
  fi

  typeset -f cyber_draw_utility_bar >/dev/null 2>&1 && cyber_draw_utility_bar
}
zle -N cyber_toggle_parallax_widget
bindkey '^[p' cyber_toggle_parallax_widget

cyber_help_widget() {
  zle -M "Keys: Alt+U topbar | Alt+D doctor | Alt+P parallax | ? query | fr cmd (foldrun)"
}
zle -N cyber_help_widget
bindkey '^[h' cyber_help_widget

cyber_search_widget() { cyber_search; zle redisplay; }
zle -N cyber_search_widget
bindkey '^[s' cyber_search_widget

cyber_clip_widget() { toggle_clipboard_bar; zle redisplay; }
zle -N cyber_clip_widget
bindkey '^[c' cyber_clip_widget

cyber_files_widget() { file_explorer; zle redisplay; }
zle -N cyber_files_widget
bindkey '^[f' cyber_files_widget

cyber_macros_widget() { macro list; zle redisplay; }
zle -N cyber_macros_widget
bindkey '^[m' cyber_macros_widget

TRAPWINCH() {
  cyber_topbar_apply_scroll_region
  typeset -f cyber_draw_utility_bar >/dev/null 2>&1 && cyber_draw_utility_bar
  parallax_redraw_now
  return 0
}
cyber_topbar_click_dispatch() {
  local x="$1" y="$2"
  (( y == 1 )) || return 1

  local rel=$(( x - CYBER_TOPBAR_START_COL + 1 ))
  (( rel < 1 )) && return 1

  local id rng a b
  for id in ${(k)CYBER_TOPBAR_BTN_RANGES}; do
    rng="${CYBER_TOPBAR_BTN_RANGES[$id]}"
    a="${rng%%:*}"
    b="${rng##*:}"
    if (( rel >= a && rel <= b )); then
      case "$id" in
        S) cyber_search ;;
        C) toggle_clipboard_bar ;;
        F) file_explorer ;;
        M) macro list ;;
        T) timeline ;;
        H) heatmap ;;
        D) cyber_toggle_doctor_widget ;;
        P) cyber_toggle_parallax_widget ;;
        Q) cyber_help_widget ;;
      esac
      return 0
    fi
  done
  return 1
}

cyber_mouse_click_widget() {
  # vine după prefixul ESC [ <
  local rest="" ch=""
  while read -rk1 ch; do
    rest+="$ch"
    [[ "$ch" == "M" || "$ch" == "m" ]] && break
  done

  # rest arată ca: "0;123;1M"
  local payload="${rest%[Mm]}"
  local b x y
  IFS=';' read -r b x y <<< "$payload"

  # doar click stânga (b=0) pe press (M)
  [[ "$rest" == *"M" ]] || return
  (( b == 0 )) || return

  zle -I
  cyber_topbar_click_dispatch "$x" "$y"
  zle redisplay
}
zle -N cyber_mouse_click_widget

# Bind pentru prefixul mouse SGR: ESC [ <
for km in emacs viins vicmd; do
  bindkey -M "$km" '^[[<' cyber_mouse_click_widget 2>/dev/null
done
typeset -g CYBER_STDERR_LOG=""
typeset -g CYBER_ORIG_STDERR_FD=""
typeset -g CYBER_LAST_CMD=""
typeset -g CYBER_CMD_START_T=0
typeset -g CYBER_VISUAL_MIN_SECONDS=2

cyber_preexec_capture_stderr() {
    [[ -o interactive ]] || return

    CYBER_TERMINAL_BUSY=1
    CYBER_CMD_START_T=$EPOCHREALTIME

    CYBER_LAST_CMD="$1"
    CYBER_STDERR_LOG="/tmp/cyber-stderr.$$"
    : >| "$CYBER_STDERR_LOG" 2>/dev/null || CYBER_STDERR_LOG=""

    cyber_disable_mouse

    # reset scroll region înainte de a rula comanda (full-screen apps)
    cyber_topbar_reset_scroll_region 2>/dev/null

    # Dacă nu putem crea log, măcar nu stricăm stderr.
    [[ -z "$CYBER_STDERR_LOG" ]] && return

    # Duplicăm stderr original ca FD separat și apoi facem tee către el
    exec {CYBER_ORIG_STDERR_FD}>&2
    exec 2> >(command tee -a "$CYBER_STDERR_LOG" >&${CYBER_ORIG_STDERR_FD})
}

cyber_precmd_restore_stderr_doctor_and_bar() {
    [[ -o interactive ]] || return
    local exit_code=$?

    CYBER_LAST_EXIT_CODE=$exit_code
    CYBER_TERMINAL_BUSY=0

    # restore stderr
    if [[ -n "${CYBER_ORIG_STDERR_FD:-}" ]]; then
        exec 2>&${CYBER_ORIG_STDERR_FD}
        exec {CYBER_ORIG_STDERR_FD}>&-
        CYBER_ORIG_STDERR_FD=""
    fi

    # citește tail din log
    local stderr_out=""
    if [[ -n "${CYBER_STDERR_LOG:-}" && -f "$CYBER_STDERR_LOG" ]]; then
        if command -v tail >/dev/null 2>&1; then
            stderr_out="$(command tail -n 120 "$CYBER_STDERR_LOG" 2>/dev/null)"
        else
            stderr_out="$(command cat "$CYBER_STDERR_LOG" 2>/dev/null)"
        fi
        command rm -f "$CYBER_STDERR_LOG" 2>/dev/null
    fi
    CYBER_STDERR_LOG=""

    # Visual confirmation fără spam:
    # - succes doar dacă a durat "mult"
    # - fail => doctor + o singură linie de error
    float dur=0
    if [[ -n "${CYBER_CMD_START_T:-}" ]]; then
        dur=$(( EPOCHREALTIME - CYBER_CMD_START_T ))
    fi

    if (( exit_code != 0 )); then
        show_error "Exit $exit_code"
        show_command_doctor "$exit_code" "$CYBER_LAST_CMD" "$stderr_out"
    else
        if (( dur >= CYBER_VISUAL_MIN_SECONDS )); then
            show_success "OK (${dur}s)"
        fi
    fi

    CYBER_LAST_CMD=""

    # topbar persistent (idle)
    if (( CYBER_TOPBAR_VISIBLE )); then
        cyber_topbar_apply_scroll_region 2>/dev/null
        cyber_enable_mouse
        cyber_draw_utility_bar 2>/dev/null
    else
        cyber_topbar_reset_scroll_region 2>/dev/null
    fi
}

# add-zsh-hook preexec cyber_preexec_capture_stderr
# add-zsh-hook precmd  cyber_precmd_restore_stderr_doctor_and_bar

alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias diff='diff --color=auto'
alias ip='ip -color=auto'
alias dmesg='dmesg --color=auto'

alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
alias -- -='cd -'
alias ~='cd ~'

alias md='mkdir -p'
alias rd='rmdir'
alias mkdir='mkdir -pv'

alias rm='rm -Iv --preserve-root'
alias mv='mv -iv'
alias cp='cp -iv'
alias ln='ln -iv'
alias chown='chown --preserve-root'
alias chmod='chmod --preserve-root'
alias chgrp='chgrp --preserve-root'

alias du='du -h'
alias df='df -h'
alias free='free -h'
alias ps='ps auxf'
alias psg='ps aux | grep -v grep | grep -i -e VSZ -e'
alias myip='curl -s https://ipinfo.io/ip'
alias localip='ip route get 1 | sed -n "s/.*src \([0-9.]*\).*/\1/p"'
alias ports='ss -tulnp'
alias meminfo='free -mlt'
alias cpuinfo='lscpu'
alias diskinfo='lsblk -o NAME,SIZE,TYPE,MOUNTPOINT'

alias h='history'
alias hg='history | grep'
alias hgi='history | grep -i'

alias c='clear'
alias q='exit'
alias :q='exit'
alias :wq='exit'

alias path='echo -e ${PATH//:/\\n}'
alias now='date +"%Y-%m-%d %H:%M:%S"'
alias week='date +%V'
alias weather='curl wttr.in'

alias vi='nvim'
alias vim='nvim'
alias v='nvim'
alias nv='nvim'
alias svi='sudo nvim'

alias zshrc='nvim ~/.zshrc'
alias bashrc='nvim ~/.bashrc'
alias vimrc='nvim ~/.config/nvim/init.lua'
alias kittyrc='nvim ~/.config/kitty/kitty.conf'
alias starshiprc='nvim ~/.config/starship.toml'
alias p10krc='nvim ~/.p10k.zsh'
alias aliasrc='nvim ~/.aliases'

alias reload='exec zsh'
alias src='source ~/.zshrc'

alias pac='sudo pacman -S'
alias pacs='pacman -Ss'
alias paci='pacman -Si'
alias pacq='pacman -Q'
alias pacqs='pacman -Qs'
alias pacqi='pacman -Qi'
alias pacql='pacman -Ql'
alias pacqo='pacman -Qo'
alias pacu='sudo pacman -Syu'
alias pacr='sudo pacman -Rns'
alias pacc='sudo pacman -Sc'
alias paccc='sudo pacman -Scc'
alias pacorphans='sudo pacman -Rns $(pacman -Qtdq)'
alias pacunlock='sudo rm /var/lib/pacman/db.lck'
alias paclog='cat /var/log/pacman.log | tail -100'
alias paclist='pacman -Qqe'
alias pacexplicit='pacman -Qqe > ~/pacman-explicit.txt'
alias pacforeign='pacman -Qm'
alias pacnative='pacman -Qn'

alias yay='yay --color=auto'
alias yayu='yay -Syu'
alias yays='yay -Ss'
alias yayi='yay -Si'
alias yayr='yay -Rns'
alias yayc='yay -Sc'
alias yaycc='yay -Scc'
alias yayorphans='yay -Rns $(yay -Qtdq)'
alias yaylist='yay -Qqe'
alias yayforeign='yay -Qm'

alias paru='paru --color=auto'
alias paruu='paru -Syu'
alias parus='paru -Ss'
alias parui='paru -Si'
alias parur='paru -Rns'
alias paruc='paru -Sc'
alias parucc='paru -Scc'

alias sc='sudo systemctl'
alias scs='sudo systemctl status'
alias scstart='sudo systemctl start'
alias scstop='sudo systemctl stop'
alias screstart='sudo systemctl restart'
alias scenable='sudo systemctl enable'
alias scdisable='sudo systemctl disable'
alias scdr='sudo systemctl daemon-reload'
alias scu='systemctl --user'
alias scus='systemctl --user status'
alias jc='journalctl'
alias jcf='journalctl -f'
alias jce='journalctl -e'
alias jcu='journalctl -u'

alias g='git'
alias ga='git add'
alias gaa='git add --all'
alias gap='git add --patch'
alias gai='git add --interactive'
alias gb='git branch'
alias gba='git branch -a'
alias gbd='git branch -d'
alias gbD='git branch -D'
alias gbm='git branch -m'
alias gbr='git branch -r'
alias gbs='git bisect'
alias gbsb='git bisect bad'
alias gbsg='git bisect good'
alias gbsr='git bisect reset'
alias gbss='git bisect start'
alias gc='git commit -v'
alias gc!='git commit -v --amend'
alias gcn!='git commit -v --amend --no-edit'
alias gca='git commit -v -a'
alias gca!='git commit -v -a --amend'
alias gcan!='git commit -v -a --amend --no-edit'
alias gcam='git commit -a -m'
alias gcmsg='git commit -m'
alias gco='git checkout'
alias gcob='git checkout -b'
alias gcom='git checkout main || git checkout master'
alias gcod='git checkout develop'
alias gcp='git cherry-pick'
alias gcpa='git cherry-pick --abort'
alias gcpc='git cherry-pick --continue'
alias gd='git diff'
alias gdc='git diff --cached'
alias gds='git diff --staged'
alias gdw='git diff --word-diff'
alias gdt='git diff-tree --no-commit-id --name-only -r'
alias gf='git fetch'
alias gfa='git fetch --all --prune'
alias gfo='git fetch origin'
alias gfu='git fetch upstream'
alias gg='git gui citool'
alias gga='git gui citool --amend'
alias ggpull='git pull origin "$(git_current_branch)"'
alias ggpush='git push origin "$(git_current_branch)"'
alias ggsup='git branch --set-upstream-to=origin/$(git_current_branch)'
alias gl='git pull'
alias glg='git log --stat'
alias glgp='git log --stat -p'
alias glgg='git log --graph'
alias glgga='git log --graph --decorate --all'
alias glgm='git log --graph --max-count=10'
alias glo='git log --oneline --decorate'
alias glog='git log --oneline --decorate --graph'
alias gloga='git log --oneline --decorate --graph --all'
alias glol='git log --graph --pretty="%Cred%h%Creset -%C(auto)%d%Creset %s %Cgreen(%ar) %C(bold blue)<%an>%Creset"'
alias glola='git log --graph --pretty="%Cred%h%Creset -%C(auto)%d%Creset %s %Cgreen(%ar) %C(bold blue)<%an>%Creset" --all'
alias glols='git log --graph --pretty="%Cred%h%Creset -%C(auto)%d%Creset %s %Cgreen(%ar) %C(bold blue)<%an>%Creset" --stat'
alias glp='git log -p'
alias gm='git merge'
alias gma='git merge --abort'
alias gmom='git merge origin/main'
alias gmod='git merge origin/develop'
alias gmum='git merge upstream/main'
alias gms='git merge --squash'
alias gmff='git merge --ff-only'
alias gp='git push'
alias gpd='git push --dry-run'
alias gpf='git push --force-with-lease'
alias gpf!='git push --force'
alias gpo='git push origin'
alias gpom='git push origin main'
alias gpoat='git push origin --all && git push origin --tags'
alias gpu='git push upstream'
alias gpv='git push -v'
alias gr='git remote'
alias gra='git remote add'
alias grb='git rebase'
alias grba='git rebase --abort'
alias grbc='git rebase --continue'
alias grbi='git rebase -i'
alias grbm='git rebase main'
alias grbd='git rebase develop'
alias grbom='git rebase origin/main'
alias grbod='git rebase origin/develop'
alias grbs='git rebase --skip'
alias grev='git revert'
alias grh='git reset'
alias grhh='git reset --hard'
alias grhs='git reset --soft'
alias grm='git rm'
alias grmc='git rm --cached'
alias grmv='git remote rename'
alias grrm='git remote remove'
alias grs='git restore'
alias grset='git remote set-url'
alias grss='git restore --source'
alias grst='git restore --staged'
alias gru='git reset --'
alias grup='git remote update'
alias grv='git remote -v'
alias gs='git status'
alias gss='git status -s'
alias gsb='git status -sb'
alias gsh='git show'
alias gsi='git submodule init'
alias gsu='git submodule update'
alias gsps='git show --pretty=short --show-signature'
alias gsta='git stash apply'
alias gstaa='git stash apply --index'
alias gstall='git stash --all'
alias gstc='git stash clear'
alias gstd='git stash drop'
alias gstl='git stash list'
alias gstp='git stash pop'
alias gsts='git stash show --text'
alias gstu='git stash --include-untracked'
alias gsw='git switch'
alias gswc='git switch -c'
alias gswm='git switch main || git switch master'
alias gswd='git switch develop'
alias gt='git tag'
alias gta='git tag -a'
alias gtd='git tag -d'
alias gtl='git tag -l'
alias gts='git tag -s'
alias gtv='git tag | sort -V'
alias gwch='git whatchanged -p --abbrev-commit --pretty=medium'
alias gwip='git add -A; git rm $(git ls-files --deleted) 2> /dev/null; git commit --no-verify --no-gpg-sign -m "--wip-- [skip ci]"'

alias lg='lazygit'
alias lzd='lazydocker'

alias d='docker'
alias dc='docker compose'
alias dcu='docker compose up'
alias dcud='docker compose up -d'
alias dcd='docker compose down'
alias dcr='docker compose restart'
alias dcl='docker compose logs'
alias dclf='docker compose logs -f'
alias dce='docker compose exec'
alias dcps='docker compose ps'
alias dcb='docker compose build'
alias dcpull='docker compose pull'

alias dps='docker ps'
alias dpsa='docker ps -a'
alias di='docker images'
alias drm='docker rm'
alias drmi='docker rmi'
alias drmf='docker rm -f'
alias drmif='docker rmi -f'
alias dex='docker exec -it'
alias dlog='docker logs'
alias dlogf='docker logs -f'
alias dinsp='docker inspect'
alias dstop='docker stop'
alias dstart='docker start'
alias drestart='docker restart'
alias dprune='docker system prune -af --volumes'
alias dvol='docker volume'
alias dnet='docker network'

alias k='kubectl'
alias kg='kubectl get'
alias kgp='kubectl get pods'
alias kgs='kubectl get services'
alias kgd='kubectl get deployments'
alias kgn='kubectl get nodes'
alias kga='kubectl get all'
alias kd='kubectl describe'
alias kdp='kubectl describe pod'
alias kds='kubectl describe service'
alias kdd='kubectl describe deployment'
alias kl='kubectl logs'
alias klf='kubectl logs -f'
alias ke='kubectl exec -it'
alias ka='kubectl apply -f'
alias kdel='kubectl delete'
alias kdelp='kubectl delete pod'
alias kdels='kubectl delete service'
alias kdeld='kubectl delete deployment'
alias kctx='kubectx'
alias kns='kubens'

alias tf='terraform'
alias tfi='terraform init'
alias tfp='terraform plan'
alias tfa='terraform apply'
alias tfaa='terraform apply -auto-approve'
alias tfd='terraform destroy'
alias tfda='terraform destroy -auto-approve'
alias tfo='terraform output'
alias tfs='terraform state'
alias tfsl='terraform state list'
alias tfss='terraform state show'
alias tfv='terraform validate'
alias tff='terraform fmt'
alias tfr='terraform refresh'
alias tfim='terraform import'
alias tfws='terraform workspace'
alias tfwsl='terraform workspace list'
alias tfwss='terraform workspace select'
alias tfwsn='terraform workspace new'
alias tfwsd='terraform workspace delete'

alias py='python'
alias py3='python3'
alias pip='pip3'
alias pipi='pip install'
alias pipir='pip install -r requirements.txt'
alias pipu='pip install --upgrade'
alias pipup='pip install --upgrade pip'
alias pipun='pip uninstall'
alias pipl='pip list'
alias piplo='pip list --outdated'
alias pipf='pip freeze'
alias pipfr='pip freeze > requirements.txt'
alias venv='python -m venv'
alias activate='source ./venv/bin/activate'
alias deact='deactivate'

alias n='npm'
alias ni='npm install'
alias nid='npm install --save-dev'
alias nig='npm install -g'
alias nu='npm update'
alias nun='npm uninstall'
alias nr='npm run'
alias nrs='npm run start'
alias nrd='npm run dev'
alias nrb='npm run build'
alias nrt='npm run test'
alias nrl='npm run lint'
alias nrw='npm run watch'
alias nci='npm ci'
alias nau='npm audit'
alias nauf='npm audit fix'
alias nl='npm list'
alias nlg='npm list -g --depth=0'
alias no='npm outdated'
alias np='npm publish'
alias nv='npm version'

alias y='yarn'
alias ya='yarn add'
alias yad='yarn add --dev'
alias yr='yarn remove'
alias yu='yarn upgrade'
alias yui='yarn upgrade-interactive'
alias ys='yarn start'
alias yd='yarn dev'
alias yb='yarn build'
alias yt='yarn test'
alias yl='yarn lint'
alias yc='yarn cache clean'

alias pn='pnpm'
alias pni='pnpm install'
alias pna='pnpm add'
alias pnad='pnpm add -D'
alias pnr='pnpm remove'
alias pnrs='pnpm run start'
alias pnrd='pnpm run dev'
alias pnrb='pnpm run build'
alias pnrt='pnpm run test'

alias cargo='cargo'
alias cb='cargo build'
alias cbr='cargo build --release'
alias cr='cargo run'
alias crr='cargo run --release'
alias ct='cargo test'
alias cc='cargo check'
alias ccl='cargo clippy'
alias cf='cargo fmt'
alias cu='cargo update'
alias ca='cargo add'
alias crm='cargo remove'
alias cdoc='cargo doc --open'
alias cw='cargo watch'
alias cwx='cargo watch -x'

alias make='make -j$(nproc)'
alias m='make'
alias mc='make clean'
alias mb='make build'
alias mi='make install'
alias mt='make test'
alias mr='make run'

alias grep='grep --color=auto'
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'
alias rg='rg --color=always --smart-case --hidden'
alias rgi='rg -i'
alias rgf='rg --files'
alias rgfh='rg --files --hidden'
alias ag='ag --color --smart-case'

alias fd='fd --color=always --hidden'
alias fdi='fd -i'
alias fdf='fd -t f'
alias fdd='fd -t d'
alias fde='fd -e'

alias cat='bat --style=plain'
alias catn='bat'
alias catp='bat -p'
alias batl='bat -l'
alias batd='bat --diff'

alias sed='sed -E'
alias awk='gawk'

alias curl='curl -w "\n"'
alias wget='wget -c'

alias rsync='rsync -avh --progress'
alias rsyncd='rsync -avh --progress --delete'
alias rsynce='rsync -avhe ssh --progress'

alias scp='scp -r'
alias sftp='sftp'

alias ssh='TERM=xterm-256color ssh'
alias sshk='ssh-keygen -t ed25519 -C'
alias ssha='ssh-add'
alias sshl='ssh-add -l'
alias sshc='cat ~/.ssh/id_ed25519.pub | xclip -selection clipboard'

alias mnt='mount | column -t'
alias umnt='umount'

alias psmem='ps auxf | sort -nr -k 4 | head -10'
alias pscpu='ps auxf | sort -nr -k 3 | head -10'
alias psg='ps aux | grep -v grep | grep -i'

alias top='htop'
alias btop='btop'
alias gtop='gotop'
alias vtop='vtop'

alias ping='ping -c 5'
alias fastping='ping -c 100 -s.2'
alias pingg='ping google.com'

alias journalctl='journalctl --no-pager'
alias logs='journalctl -f'

alias speedtest='curl -s https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py | python -'

alias openports='netstat -tulanp'
alias listening='lsof -i -P -n | grep LISTEN'
alias connections='ss -tulanp'

alias yt='yt-dlp'
alias ytv='yt-dlp -f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" --merge-output-format mp4'
alias yta='yt-dlp -x --audio-format mp3'
alias ytp='yt-dlp -o "%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s"'

alias android='scrcpy'
alias adb='adb'
alias fastboot='fastboot'

alias mountiso='sudo mount -o loop'
alias umountiso='sudo umount'

alias update-grub='sudo grub-mkconfig -o /boot/grub/grub.cfg'
alias update-initramfs='sudo mkinitcpio -P'

alias fontcache='fc-cache -fv'
alias fontlist='fc-list'
alias fontmatch='fc-match'

alias xclip='xclip -selection clipboard'
alias xpaste='xclip -selection clipboard -o'

alias wlcopy='wl-copy'
alias wlpaste='wl-paste'

alias qr='qrencode -t ansiutf8'
alias qrclip='xclip -selection clipboard -o | qrencode -t ansiutf8'

alias serve='python -m http.server 8000'
alias servephp='php -S localhost:8000'

alias timestamp='date +%s'
alias datestamp='date +%Y%m%d'
alias datetime='date "+%Y-%m-%d %H:%M:%S"'

alias calc='bc -l'
alias math='python -c "from math import *; print(eval(input()))"'

alias urlencode='python -c "import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1]))"'
alias urldecode='python -c "import sys, urllib.parse; print(urllib.parse.unquote(sys.argv[1]))"'

alias base64e='base64'
alias base64d='base64 -d'

alias sha256='shasum -a 256'
alias sha512='shasum -a 512'
alias md5='md5sum'

alias genpass='openssl rand -base64 32'
alias genpassw='openssl rand -base64 32 | tr -d "=+/" | cut -c1-16'
alias genpassen='tr -dc "A-Za-z0-9!@#$%^&*()_+=-" < /dev/urandom | head -c 32'

alias uuid='uuidgen'
alias uuidl='uuidgen | tr "[:upper:]" "[:lower:]"'

alias tolower='tr "[:upper:]" "[:lower:]"'
alias toupper='tr "[:lower:]" "[:upper:]"'

alias randword='shuf -n 1 /usr/share/dict/words'
alias randwords='shuf -n 5 /usr/share/dict/words'

alias colors='for i in {0..255}; do printf "\x1b[38;5;${i}mcolor%-5i\x1b[0m" $i; if ! (( ($i + 1) % 8 )); then echo; fi; done'
alias colortest='curl -s https://raw.githubusercontent.com/pablopunk/colortest/master/colortest | bash'
alias truecolor='printf "\x1b[38;2;255;100;0mTRUECOLOR\x1b[0m\n"'

alias matrix='cmatrix -b -u 4 -C cyan'
alias fire='aafire -driver curses'
alias pipes='pipes.sh'
alias rain='rain'
alias clock='tty-clock -c -C 6 -f "%A, %B %d %Y"'
alias nyancat='nyancat'
alias asciiquarium='asciiquarium'
alias cava='cava'
alias neofetch='neofetch'
alias screenfetch='screenfetch'
alias pfetch='pfetch'
alias fastfetch='fastfetch'

alias please='sudo'
alias fucking='sudo'
alias pls='sudo'

alias fucking-dns='sudo systemctl restart systemd-resolved'
alias fucking-network='sudo systemctl restart NetworkManager'
alias fucking-bluetooth='sudo systemctl restart bluetooth'
alias fucking-sound='pulseaudio -k && pulseaudio --start'
ERROR_MESSAGES=(
    "'%s' is not a command. This was optimistic."
    "The system searched briefly, then gave up on '%s'."
    "'%s' does not exist in any reasonable interpretation of reality."
    "Command '%s' failed before it even had a chance."
    "There is no universe where '%s' works."
    "'%s' was typed confidently. That was the mistake."
    "Command '%s' produced disappointment at scale."
    "The shell refuses to enable whatever '%s' was supposed to be."
    "'%s' looks like a command. It is not."
    "Nothing here answers to '%s'. Try reality."
    "Command '%s' cannot be resolved. Nor should it be."
    "The system parsed '%s' and felt nothing."
    "'%s' lacks both purpose and implementation."
    "Command '%s' is syntactically present and functionally absent."
    "Execution aborted. '%s' had no executable intent."
    "The shell evaluated '%s' and moved on."
    "No subsystem volunteered to handle '%s'."
    "'%s' failed silently. You just happened to notice."
    "'%s' is just noise."
    "Command '%s' exists only as entropy."
    "There is no action associated with '%s'."
    "'%s' was reduced to characters and discarded."
    "The machine does not recognize '%s' as a request."
    "Nothing changed as a result of '%s'."
    "'%s' left no trace."
    "Stop typing '%s'."
    "'%s' again? No."
    "Command '%s' was rejected immediately."
    "This is not how '%s' works. Or anything."
    "'%s' failed faster than expected."
    "The system will not entertain '%s'."
    "Command '%s' has been ignored."
)

SUCCESS_MESSAGES=(
    "Done."
    "Completed."
    "Finished."
    "Executed."
    "Operation succeeded."
    "Command completed."
    "Result produced."
    "Task finished without incident."
)

git_current_branch() {
    git rev-parse --abbrev-ref HEAD 2>/dev/null
}

git_repo_name() {
    basename $(git rev-parse --show-toplevel 2>/dev/null) 2>/dev/null
}

git_is_dirty() {
    [[ -n $(git status --porcelain 2>/dev/null) ]]
}

git_commits_ahead() {
    git rev-list --count @{upstream}..HEAD 2>/dev/null || echo 0
}

git_commits_behind() {
    git rev-list --count HEAD..@{upstream} 2>/dev/null || echo 0
}

git_stash_count() {
    git stash list 2>/dev/null | wc -l
}

gclone() {
    git clone --depth 1 "$@"
}

gfork() {
    local repo="$1"
    local user=$(echo "$repo" | cut -d'/' -f1)
    local name=$(echo "$repo" | cut -d'/' -f2)
    gh repo fork "$repo" --clone
}

gweb() {
    local url=$(git config --get remote.origin.url)
    url=${url/git@github.com:/https://github.com/}
    url=${url/git@gitlab.com:/https://gitlab.com/}
    url=${url%.git}
    xdg-open "$url" 2>/dev/null || open "$url" 2>/dev/null
}

gpr() {
    local branch=$(git_current_branch)
    gh pr create --base main --head "$branch" "$@"
}

gissue() {
    gh issue create "$@"
}

grel() {
    local version=$1
    git tag -a "v$version" -m "Release v$version"
    git push origin "v$version"
}


portinfo() {
    local port=$1
    lsof -i:"$port" 2>/dev/null || ss -tulnp | grep ":$port "
}

memusage() {
    ps aux --sort=-%mem | head -n "${1:-10}"
}

cpuusage() {
    ps aux --sort=-%cpu | head -n "${1:-10}"
}

proc() {
    ps aux | grep -i "$1" | grep -v grep
}
lns() {
    ln -sfv "$1" "$2"
}

largest() {
    local count=${1:-10}
    du -ah . 2>/dev/null | sort -rh | head -n "$count"
}

newest() {
    local count=${1:-10}
    find . -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -n "$count" | cut -d' ' -f2-
}

oldest() {
    local count=${1:-10}
    find . -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | head -n "$count" | cut -d' ' -f2-
}

empty() {
    find . -type f -empty 2>/dev/null
}

duplicates() {
    find . -type f -exec md5sum {} + 2>/dev/null | sort | uniq -w32 -dD
}


findfile() {
    fd "$@" 2>/dev/null || find . -name "*$1*" 2>/dev/null
}

findtext() {
    rg "$@" 2>/dev/null || grep -r "$1" . 2>/dev/null
}
mkcd() {
    mkdir -p "$1" && cd "$1"
}

cdls() {
    cd "$1" && ls
}
cheatsheet() {
    curl -s "cheat.sh/$1"
}

explain() {
    curl -s "https://explainshell.com/explain?cmd=$(echo "$*" | jq -sRr @uri)"
}

qrcode() {
    curl -s "qrcode.show/$1"
}

dict() {
    curl -s "dict://dict.org/d:$1"
}

ipinfo() {
    curl -s "https://ipinfo.io/$1"
}

shorten() {
    curl -s "https://is.gd/create.php?format=simple&url=$1"
}

rate() {
    curl -s "https://api.exchangerate-api.com/v4/latest/${1:-USD}" | jq
}

randomquote() {
    curl -s "https://api.quotable.io/random" | jq -r '"\(.content)" - \(.author)'
}

randomfact() {
    curl -s "https://uselessfacts.jsph.pl/random.json?language=en" | jq -r '.text'
}

randomjoke() {
    curl -s "https://official-joke-api.appspot.com/random_joke" | jq -r '"\(.setup)\n\(.punchline)"'
}
hex2dec() {
    printf "%d\n" "$1"
}

dec2hex() {
    printf "0x%x\n" "$1"
}

bin2dec() {
    echo $((2#$1))
}

dec2bin() {
    echo "obase=2; $1" | bc
}

rgb2hex() {
    printf "#%02x%02x%02x\n" "$1" "$2" "$3"
}
gradient_text() {
    local text=$1
    local start_r=0 start_g=255 start_b=255
    local end_r=255 end_g=0 end_b=255
    local len=${#text}

    for ((i=0; i<len; i++)); do
        local ratio=$((i * 100 / len))
        local r=$((start_r + (end_r - start_r) * ratio / 100))
        local g=$((start_g + (end_g - start_g) * ratio / 100))
        local b=$((start_b + (end_b - start_b) * ratio / 100))
        printf "\033[38;2;%d;%d;%dm%s" "$r" "$g" "$b" "${text:i:1}"
    done
    printf "\033[0m\n"
}

rainbow_text() {
    local text=$1
    local colors=(196 208 226 46 51 21 201)
    local len=${#text}

    for ((i=0; i<len; i++)); do
        local color_idx=$((i % ${#colors[@]}))
        printf "\033[38;5;%dm%s" "${colors[$color_idx]}" "${text:i:1}"
    done
    printf "\033[0m\n"
}
typing_effect() {
    local text=$1
    local delay=${2:-0.05}

    for ((i=0; i<${#text}; i++)); do
        printf "%s" "${text:i:1}"
        sleep "$delay"
    done
    printf "\n"
}


# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
# SECTION 12: FEATURE 1 - DYNAMIC GRADIENT PROMPT
# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550

# Gradient animation state
typeset -g GRADIENT_PHASE=0
typeset -g GRADIENT_DIRECTION=1
typeset -g GRADIENT_SPEED=0.1

# Calculate gradient color based on state
calculate_gradient_color() {
  local position="$1" phase="$2" exit_code="$3" cpu_load="$4" battery_level="$5"

  # strip ANSI \e[ ... letter
  local ansi_pat=$'\e''\[[0-9;]##[[:alpha:]]'
  position="${position//$~ansi_pat/}"
  phase="${phase//$~ansi_pat/}"
  exit_code="${exit_code//$~ansi_pat/}"
  cpu_load="${cpu_load//$~ansi_pat/}"
  battery_level="${battery_level//$~ansi_pat/}"

  # cpu_load: ia doar primul număr dacă vine "0.25 0.18 0.15"
  cpu_load="${cpu_load%% *}"

  # keep only numeric forms
  position="${position//[^0-9-]/}"
  phase="${phase//[^0-9-]/}"
  exit_code="${exit_code//[^0-9-]/}"
  cpu_load="${cpu_load//[^0-9.]/}"
  battery_level="${battery_level//[^0-9]/}"

  # defaults
  [[ -n "$position" ]] || position=0
  [[ -n "$phase" ]] || phase=0
  [[ -n "$exit_code" ]] || exit_code=0
  [[ -n "$cpu_load" ]] || cpu_load=0
  [[ -n "$battery_level" ]] || battery_level=0

  # typed vars (AICI contează)
  local -i ipos=position iph=phase iexit=exit_code ibatt=battery_level
  local -F icpu=cpu_load

  # Base colors
  local -i start_r=0 start_g=255 start_b=255
  local -i end_r=255 end_g=0 end_b=255

  # State shifts
  if (( iexit != 0 )); then
    start_r=255 start_g=50  start_b=50
    end_r=255   end_g=100  end_b=0
  elif (( icpu > 2.0 )); then
    start_r=255 start_g=200 start_b=0
    end_r=255   end_g=100  end_b=0
  elif (( ibatt < 20 )); then
    start_r=255 start_g=180 start_b=0
    end_r=255   end_g=100  end_b=50
  fi

  local -i animated_pos=$(( (ipos + iph) % 100 ))
  local -i r=$(( start_r + (end_r - start_r) * animated_pos / 100 ))
  local -i g=$(( start_g + (end_g - start_g) * animated_pos / 100 ))
  local -i b=$(( start_b + (end_b - start_b) * animated_pos / 100 ))

  printf "%%F{#%02x%02x%02x}" "$r" "$g" "$b"
}

# Generate animated gradient text
gradient_text_animated() {
    local text="$1"
    local len=${#text}
    local result=""

    get_cpu_load >/dev/null
    get_battery_info

    for ((i=0; i<len; i++)); do
        local pos=$((i * 100 / len))
        local color=$(calculate_gradient_color $pos $GRADIENT_PHASE $CYBER_LAST_EXIT_CODE $CYBER_CPU_LOAD $CYBER_BATTERY_LEVEL)
        result+="${color}${text:$i:1}"
    done

    printf "%s%%f" "$result"
}

# Update gradient phase (called in background)
update_gradient_phase() {
    while true; do
        GRADIENT_PHASE=$(( (GRADIENT_PHASE + GRADIENT_DIRECTION * 2) % 100 ))
        sleep "$GRADIENT_SPEED"
    done
}

# Prompt gradient dimming on Enter
dim_prompt_gradient() {
    # This creates a "fade out" effect
    local fade_steps=5
    for ((i=fade_steps; i>=0; i--)); do
        local dim_factor=$((i * 20))
        # Would update prompt here with dimmed colors
        sleep 0.02
    done
}
typeset -g CYBER_GIT_PROMPT_CACHE_PWD=""
typeset -g CYBER_GIT_PROMPT_CACHE_T=0
typeset -g CYBER_GIT_PROMPT_CACHE_VAL=""

cyber_git_prompt_part() {
  local now=$EPOCHSECONDS
  if [[ "$PWD" == "$CYBER_GIT_PROMPT_CACHE_PWD" && $(( now - CYBER_GIT_PROMPT_CACHE_T )) -lt 2 ]]; then
    print -r -- "$CYBER_GIT_PROMPT_CACHE_VAL"
    return 0
  fi

  local val=""
  if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    local branch="$(git branch --show-current 2>/dev/null)"
    if [[ -n "$branch" ]]; then
      local dirty=""
      git diff --quiet 2>/dev/null || dirty="●"
      val="  ⎇ ${branch}${dirty}"
    fi
  fi

  CYBER_GIT_PROMPT_CACHE_PWD="$PWD"
  CYBER_GIT_PROMPT_CACHE_T=$now
  CYBER_GIT_PROMPT_CACHE_VAL="$val"
  print -r -- "$val"
}
# Enhanced gradient prompt generation
generate_gradient_prompt() {
  local exit_code=$CYBER_LAST_EXIT_CODE

  get_cpu_load >/dev/null
  get_battery_info

  local cols=${COLUMNS:-80}
  local inner=$(( cols - 4 ))
  (( inner < 20 )) && inner=20

  local time_str="$(date '+%H:%M')"
  local dir_short="${PWD/#$HOME/~}"

  local git_part="$(cyber_git_prompt_part)"

  local status_part=""
  if (( CYBER_BATTERY_LEVEL < 20 && CYBER_BATTERY_CHARGING == 0 )); then
    status_part+="  ⚡${CYBER_BATTERY_LEVEL}%"
  fi
  if (( CYBER_CPU_LOAD > 2.0 )); then
    status_part+="  ◐${CYBER_CPU_LOAD}"
  fi
  if (( exit_code != 0 )); then
    status_part+="  ✖${exit_code}"
  else
    status_part+="  ✓"
  fi

  local text="⟦${time_str}⟧  ${dir_short}${git_part}${status_part}"
  if (( ${#text} > inner )); then
    text="${text[1,$inner]}"
  fi
  local pad=$(( inner - ${#text} ))
  (( pad < 0 )) && pad=0
  local pad_spaces=""
  (( pad > 0 )) && pad_spaces="$(printf "%*s" "$pad" "")"

  local border="%F{#00ffff}"
  local line1="${border}╭─%f$(gradient_text_animated "$text")${border}${pad_spaces}─╮%f"

  local arrow=""
  if (( exit_code == 0 )); then
    arrow="$(gradient_text_animated "❯")"
  else
    arrow="%F{#ff3232}❯%f"
  fi

  # linia 2 începe box-ul de input; închidem cu RPROMPT (setat mai jos)
  local line2="${border}╰─%f ${arrow} "

  print -n -- "${line1}\n${line2}"
}
setopt prompt_subst
PROMPT='$(generate_gradient_prompt)'
RPROMPT='%F{#00ffff}╯%f'

# pornește animația (o singură dată)
if [[ -o interactive ]]; then
  if [[ -z "${CYBER_GRADIENT_PID:-}" ]] || ! kill -0 "$CYBER_GRADIENT_PID" 2>/dev/null; then
    update_gradient_phase &!
    CYBER_GRADIENT_PID=$!
  fi
fi
# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
# SECTION 15: FEATURE 4 - CINEMATIC INTRO
# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550

# Intro skip flag
typeset -g INTRO_SKIPPED=0

# ASCII Art frames for animation
typeset -ga INTRO_FRAMES

# Frame 1 - Empty
INTRO_FRAMES[1]=""

# Frame 2 - Initial glow
INTRO_FRAMES[2]='
                              ░░░░░░
                            ░░░░░░░░░░
                          ░░░░░░░░░░░░░░
'

# Frame 3 - Logo forming
INTRO_FRAMES[3]='
                              ▒▒▒▒▒▒
                            ▒▒▒▒▒▒▒▒▒▒
                          ▒▒▒▒▒▒▒▒▒▒▒▒▒▒
                            ▒▒▒▒▒▒▒▒▒▒
                              ▒▒▒▒▒▒
'

# Full Arch Linux logo ASCII art
INTRO_ARCH_LOGO='
                                     /\
                                    /  \
                                   /    \
                                  /      \
                                 /   /\   \
                                /   /  \   \
                               /   /    \   \
                              /   /      \   \
                             /   /   /\   \   \
                            /   /   /  \   \   \
                           /   /   / /\ \   \   \
                          /   /   / /  \ \   \   \
                         /   /   / /    \ \   \   \
                        /   /   / /      \ \   \   \
                       /   /   / /        \ \   \   \
                      /   /___/ /__________\ \___\   \
                     /________________________________\
'

# Cyberpunk-styled Arch logo
INTRO_CYBER_ARCH='


                  ◢◣
                 ◢██◣◥░
                ◢████◣◥░
               ◢██◤◥██◣◥░
              ◢██◤  ◥██◣◥░
             ◢██◤ ◢◣ ◥██◣◥░
            ◢██◤ ◢██◣ ◥██◣◥░
           ◢██◤ ◢████◣ ◥██◣◥░
          ◢██◤ ◢██◤◥██◣ ◥██◣◥░
         ◢██◤ ◢██◤  ◥██◣ ◥██◣◥░
        ◥██◤ ◥██◤    ◥██◣ ◥██◣█◤
          ◥░   ◥░      ◥██◣ ◢█◤
           ◥░   ◥░      ◥███◤
'

# Welcome text
INTRO_WELCOME_TEXT='

╔═╗╔═╗╔═╗╦ ╦  ╦  ╦╔╗╔╦ ╦═╗ ╦
╠═╣╠╦╝║  ╠═╣  ║  ║║║║║ ║╔╩╦╝
╩ ╩╩╚═╚═╝╩ ╩  ╩═╝╩╝╚╝╚═╝╩ ╚═
────────────────────────────
'



# Intro sound effect (using system beep or external command)
play_intro_sound() {
    if command -v paplay &>/dev/null && [[ -f "$CYBER_DATA_DIR/sounds/intro.wav" ]]; then
        paplay "$CYBER_DATA_DIR/sounds/intro.wav" &
    elif command -v aplay &>/dev/null && [[ -f "$CYBER_DATA_DIR/sounds/intro.wav" ]]; then
        aplay -q "$CYBER_DATA_DIR/sounds/intro.wav" &
    fi
}

# Check for keypress to skip intro
check_skip_intro() {
    local key
    if read -t 0.01 -k1 key 2>/dev/null; then
        INTRO_SKIPPED=1
        return 0
    fi
    return 1
}

# Print with typing effect
type_text() {
    local text="$1"
    local delay=${2:-0.03}
    local color="${3:-cyan}"

    printf "%b" "${CYBER_COLORS[$color]}"
    for ((i=0; i<${#text}; i++)); do
        check_skip_intro && break
        printf "%s" "${text:$i:1}"
        sleep "$delay"
    done
    printf "%b\n" "${CYBER_STYLE[reset]}"
}

# Glow animation effect
glow_effect() {
    local text="$1"
    local glow_steps=5
    local colors=(240 244 248 252 255)

    for color in "${colors[@]}"; do
        check_skip_intro && break
        printf "\r\033[38;5;%dm%s\033[0m" "$color" "$text"
        sleep 0.05
    done
    printf "\n"
}

# Scan line effect
scan_line_effect() {
    local lines=("$@")
    local total=${#lines[@]}

    for ((i=0; i<total; i++)); do
        check_skip_intro && break
        printf "%b%s%b\n" "${CYBER_COLORS[cyan]}" "${lines[$((i+1))]}" "${CYBER_STYLE[reset]}"
        sleep 0.02
    done
}

# Full cinematic intro
cinematic_intro() {
    # Check if intro already shown or should be skipped
    [[ $WELCOME_SHOWN -eq 1 ]] && return
    [[ $SKIP_INTRO -eq 1 ]] && return

    # Clear screen
    clear

    # Hide cursor
    printf '\033[?25l'

    # Play sound (optional)
    play_intro_sound

    # Boot sequence simulation
    local boot_messages=(
        "Initializing CYBER_SHELL v2.0..."
        "Loading neural interface..."
        "Connecting to the grid..."
        "Authenticating user: $USER"
        "Loading personal configuration..."
        "Establishing secure connection..."
        "Neural link established."
    )

    printf "\n"
    for msg in "${boot_messages[@]}"; do
        check_skip_intro && break
        printf "  %b[%b✓%b]%b %s\n" \
            "${CYBER_COLORS[dark]}" \
            "${CYBER_COLORS[green]}" \
            "${CYBER_COLORS[dark]}" \
            "${CYBER_STYLE[reset]}" \
            "$msg"
        sleep 0.15
    done

    [[ $INTRO_SKIPPED -eq 1 ]] && { printf '\033[?25h'; return; }

    sleep 0.3
    clear

    # Animated logo appearance
    printf "\n"
    printf "  %b" "${CYBER_COLORS[cyan]}"

    # Print logo with scan effect
    local -a logo_lines
    while IFS= read -r line; do
        logo_lines+=("$line")
    done <<< "$INTRO_CYBER_ARCH"

    for line in "${logo_lines[@]}"; do
        check_skip_intro && break
        printf "%s\n" "$line"
        sleep 0.015
    done

    printf "%b" "${CYBER_STYLE[reset]}"

    [[ $INTRO_SKIPPED -eq 1 ]] && { printf '\033[?25h'; return; }

    # Print welcome text with glow
    printf "\n"
    local -a welcome_lines
    while IFS= read -r line; do
        welcome_lines+=("$line")
    done <<< "$INTRO_WELCOME_TEXT"

    for line in "${welcome_lines[@]}"; do
        check_skip_intro && break
        glow_effect "$line"
    done

    [[ $INTRO_SKIPPED -eq 1 ]] && { printf '\033[?25h'; return; }

    # System info box
    printf "\n"
    printf "  %b╭───────────────────────────────────────────────────────────────────────────╮%b\n" \
        "${CYBER_COLORS[magenta]}" "${CYBER_STYLE[reset]}"
    printf "  %b│%b  %b📅%b %s                                           %b│%b\n" \
        "${CYBER_COLORS[magenta]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}" \
        "$(date '+%A, %d %B %Y')" \
        "${CYBER_COLORS[magenta]}" "${CYBER_STYLE[reset]}"
    printf "  %b│%b  %b🖥️%b  %s @ %s                                    %b│%b\n" \
        "${CYBER_COLORS[magenta]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[green]}" "${CYBER_STYLE[reset]}" \
        "$(hostname)" "$(uname -sr | cut -d' ' -f1-2)" \
        "${CYBER_COLORS[magenta]}" "${CYBER_STYLE[reset]}"
    printf "  %b│%b  %b⏰%b %s                                                      %b│%b\n" \
        "${CYBER_COLORS[magenta]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}" \
        "$(date '+%H:%M:%S')" \
        "${CYBER_COLORS[magenta]}" "${CYBER_STYLE[reset]}"
    printf "  %b│%b  %b💾%b Memory: %s                                          %b│%b\n" \
        "${CYBER_COLORS[magenta]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[purple]}" "${CYBER_STYLE[reset]}" \
        "$(free -h | awk '/Mem:/ {print $3 "/" $2}')" \
        "${CYBER_COLORS[magenta]}" "${CYBER_STYLE[reset]}"
    printf "  %b│%b  %b💽%b Disk: %s                                        %b│%b\n" \
        "${CYBER_COLORS[magenta]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[orange]}" "${CYBER_STYLE[reset]}" \
        "$(df -h / | awk 'NR==2 {print $3 "/" $2}')" \
        "${CYBER_COLORS[magenta]}" "${CYBER_STYLE[reset]}"
    printf "  %b╰───────────────────────────────────────────────────────────────────────────╯%b\n" \
        "${CYBER_COLORS[magenta]}" "${CYBER_STYLE[reset]}"

    printf "\n"

    # Show Tree (added)
    if [[ -f /workspace/brad_tui.py ]]; then
        timeout 5s python3 /workspace/brad_tui.py 2>/dev/null
        clear
    elif [[ -f brad_tui.py ]]; then
        timeout 5s python3 brad_tui.py 2>/dev/null
        clear
    fi

    # Final welcome message with gradient
    local welcome_msg="    Welcome to the CYBERPUNK SHELL EXPERIENCE    "
    gradient_text_animated "$welcome_msg"

    printf "\n"

    # Show cursor
    printf '\033[?25h'
# Clear pentru parallax
    clear

    # Mark as shown
    WELCOME_SHOWN=1
}

# Quick welcome (non-cinematic)
quick_welcome() {
    printf "\n"
    gradient_text_animated "  ⚡ CYBER SHELL READY ⚡  "
    printf "\n"
}



# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
# SECTION 16: FEATURE 5 - PARALLAX & DEPTH ILLUSION
# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
typeset -g PARALLAX_ENABLED=${PARALLAX_ENABLED:-1}
typeset -g PARALLAX_BG_OFFSET=0
typeset -gi PARALLAX_PX=0
typeset -gi PARALLAX_PY=0
typeset -g PARALLAX_PID=""
typeset -ga STAR_POSITIONS=()
typeset -gi STARS_DRAWN=0

# Depth layers (compatibilitate)
typeset -gA DEPTH_LAYERS
DEPTH_LAYERS=([background]=1 [output]=2 [prompt]=3 [overlay]=4)

typeset -gA LAYER_COLORS
LAYER_COLORS=(
    [bg_dim]="\033[38;2;40;45;60m"
    [bg_med]="\033[38;2;70;90;120m"
    [bg_bright]="\033[38;2;120;180;220m"
    [background]="\033[38;2;50;55;75m"
    [output]="\033[38;2;180;180;190m"
    [prompt]="\033[38;2;125;249;255m"
    [overlay]="\033[38;2;0;255;255m"
)

apply_depth_effect() {
    local text="$1" layer="${2:-output}"
    printf "%b%s%b" "${LAYER_COLORS[$layer]}" "$text" "${CYBER_STYLE[reset]}"
}

parallax_scroll() {
    PARALLAX_BG_OFFSET=$((PARALLAX_BG_OFFSET + ${1:-1} * ${2:-1}))
}

# Generează și desenează stelele O SINGURĂ DATĂ
_draw_static_stars() {
  [[ -t 1 ]] || return
  (( STARS_DRAWN )) && return

  local cols=${COLUMNS:-80} lines=${LINES:-24}
  local num_stars=$(( cols * lines / 35 ))
  local i h x y brightness char r g b color_type

  STAR_POSITIONS=()

  printf '\e[s'

  for ((i=0; i<num_stars; i++)); do
    h=$(( (1103515245 * (i * 7919 + 104729) + 12345) & 0x7FFFFFFF ))
    x=$(( (h % (cols - 4)) + 3 ))
    h=$(( (h * 16807 + 1) & 0x7FFFFFFF ))
    y=$(( (h % (lines - 6)) + 4 ))

    # Salvează și tipul de culoare
    color_type=$(( h % 8 ))
    STAR_POSITIONS+=("$x:$y:$color_type")

    brightness=$(( (h * 13) % 100 ))

    # Caracter bazat pe brightness
    if (( brightness > 85 )); then
      char="✦"
    elif (( brightness > 65 )); then
      char="•"
    elif (( brightness > 45 )); then
      char="∙"
    elif (( brightness > 25 )); then
      char="·"
    else
      char="."
    fi

    # CULORI DIFERITE pentru fiecare stea
    case $color_type in
      0) # Cyan
        r=$(( 40 + brightness )); g=$(( 180 + brightness/2 )); b=$(( 220 + brightness/3 )) ;;
      1) # Magenta/Roz
        r=$(( 180 + brightness/2 )); g=$(( 50 + brightness/2 )); b=$(( 180 + brightness/2 )) ;;
      2) # Galben/Auriu
        r=$(( 200 + brightness/3 )); g=$(( 180 + brightness/3 )); b=$(( 40 + brightness/3 )) ;;
      3) # Verde
        r=$(( 40 + brightness/2 )); g=$(( 180 + brightness/2 )); b=$(( 80 + brightness/2 )) ;;
      4) # Portocaliu
        r=$(( 220 + brightness/4 )); g=$(( 120 + brightness/3 )); b=$(( 30 + brightness/4 )) ;;
      5) # Albastru
        r=$(( 60 + brightness/2 )); g=$(( 100 + brightness/2 )); b=$(( 200 + brightness/3 )) ;;
      6) # Alb/Argintiu
        r=$(( 160 + brightness/2 )); g=$(( 170 + brightness/2 )); b=$(( 190 + brightness/2 )) ;;
      7) # Roșu
        r=$(( 200 + brightness/3 )); g=$(( 50 + brightness/3 )); b=$(( 60 + brightness/3 )) ;;
    esac

    (( r > 255 )) && r=255; (( g > 255 )) && g=255; (( b > 255 )) && b=255
    printf '\e[%d;%dH\e[38;2;%d;%d;%dm%s' "$y" "$x" "$r" "$g" "$b" "$char"
  done

  printf '\e[0m\e[u'
  STARS_DRAWN=1
}

# Pâlpâit LENT - schimbă doar câteva stele, PĂSTREAZĂ CULOAREA
_twinkle_few_stars() {
  [[ -t 1 ]] || return
  (( ${#STAR_POSITIONS[@]} == 0 )) && return

  local total=${#STAR_POSITIONS[@]}
  local to_twinkle=$(( total / 12 + 1 ))
  local i idx pos x y color_type brightness char r g b

  printf '\e[s'

  for ((i=0; i<to_twinkle; i++)); do
    idx=$(( RANDOM % total + 1 ))
    pos="${STAR_POSITIONS[$idx]}"
    x=${pos%%:*}
    local rest=${pos#*:}
    y=${rest%%:*}
    color_type=${rest##*:}

    brightness=$(( RANDOM % 100 ))

    # Caracter bazat pe brightness
    if (( brightness > 85 )); then
      char="✦"
    elif (( brightness > 60 )); then
      char="•"
    elif (( brightness > 35 )); then
      char="∙"
    elif (( brightness > 15 )); then
      char="·"
    else
      char="."
    fi

    # Aceeași culoare ca la generare, dar cu brightness diferit
    case $color_type in
      0) # Cyan
        r=$(( 30 + brightness )); g=$(( 150 + brightness/2 )); b=$(( 200 + brightness/3 )) ;;
      1) # Magenta/Roz
        r=$(( 150 + brightness/2 )); g=$(( 40 + brightness/2 )); b=$(( 150 + brightness/2 )) ;;
      2) # Galben/Auriu
        r=$(( 180 + brightness/3 )); g=$(( 150 + brightness/3 )); b=$(( 30 + brightness/4 )) ;;
      3) # Verde
        r=$(( 30 + brightness/2 )); g=$(( 150 + brightness/2 )); b=$(( 60 + brightness/2 )) ;;
      4) # Portocaliu
        r=$(( 200 + brightness/4 )); g=$(( 100 + brightness/3 )); b=$(( 20 + brightness/5 )) ;;
      5) # Albastru
        r=$(( 50 + brightness/2 )); g=$(( 80 + brightness/2 )); b=$(( 180 + brightness/3 )) ;;
      6) # Alb/Argintiu
        r=$(( 140 + brightness/2 )); g=$(( 150 + brightness/2 )); b=$(( 170 + brightness/2 )) ;;
      7) # Roșu
        r=$(( 180 + brightness/3 )); g=$(( 40 + brightness/4 )); b=$(( 50 + brightness/4 )) ;;
    esac

    (( r > 255 )) && r=255; (( g > 255 )) && g=255; (( b > 255 )) && b=255
    printf '\e[%d;%dH\e[38;2;%d;%d;%dm%s' "$y" "$x" "$r" "$g" "$b" "$char"
  done

  printf '\e[0m\e[u'
}

parallax_tick() {
  _draw_static_stars
  # Disabled async loop to prevent overlapping text
  # while (( PARALLAX_ENABLED )); do
  #   sleep 0.4
  #   _twinkle_few_stars
  # done
}

parallax_start() {
  (( PARALLAX_ENABLED )) || return
  if [[ -z "$PARALLAX_PID" ]] || ! kill -0 "$PARALLAX_PID" 2>/dev/null; then
    parallax_tick &!
    PARALLAX_PID=$!
  fi
}

parallax_stop() {
  [[ -n "$PARALLAX_PID" ]] && kill "$PARALLAX_PID" 2>/dev/null
  PARALLAX_PID=""
}

parallax_redraw_now() {
  STARS_DRAWN=0
  _draw_static_stars
}

# Funcții de compatibilitate
generate_parallax_bg() { _draw_static_stars; }
parallax_draw_fullscreen_skip() { :; }
cyber_draw_parallax_header() { :; }

cyber_toggle_parallax_widget() {
  (( PARALLAX_ENABLED = !PARALLAX_ENABLED ))
  if (( PARALLAX_ENABLED )); then
    parallax_start
    zle -M "✦ Stars: ON"
  else
    parallax_stop
    zle -M "✦ Stars: OFF"
  fi
}
zle -N cyber_toggle_parallax_widget
bindkey '^[p' cyber_toggle_parallax_widget
#\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
# SECTION 17: FEATURE 6 - NLP FOR COMMAND CORRECTIONS
# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550

# NLP dictionary - common typos and corrections
typeset -gA NLP_TYPO_MAP
NLP_TYPO_MAP=(
    # Common typos
    ["suod"]="sudo"
    ["sduo"]="sudo"
    ["sud"]="sudo"
    ["suo"]="sudo"
    ["sudp"]="sudo"
    ["pacmna"]="pacman"
    ["pacmn"]="pacman"
    ["pacan"]="pacman"
    ["apcman"]="pacman"
    ["pcaman"]="pacman"
    ["grpe"]="grep"
    ["gerp"]="grep"
    ["gre"]="grep"
    ["cta"]="cat"
    ["caat"]="cat"
    ["ct"]="cat"
    ["lls"]="ls"
    ["lss"]="ls"
    ["sl"]="ls"
    ["sl"]="ls"
    ["cdd"]="cd"
    ["ccd"]="cd"
    ["dc"]="cd"
    ["mkdr"]="mkdir"
    ["mkidr"]="mkdir"
    ["mdkir"]="mkdir"
    ["mkadir"]="mkdir"
    ["touhc"]="touch"
    ["toch"]="touch"
    ["tuoch"]="touch"
    ["pytohn"]="python"
    ["pyton"]="python"
    ["pythno"]="python"
    ["pytho"]="python"
    ["gti"]="git"
    ["igt"]="git"
    ["gi"]="git"
    ["nivm"]="nvim"
    ["nvi"]="nvim"
    ["vnim"]="nvim"
    ["nmiv"]="nvim"
    ["yaay"]="yay"
    ["yya"]="yay"
    ["ay"]="yay"
    ["paru"]="paru"
    ["apru"]="paru"
    ["prau"]="paru"
    ["clar"]="clear"
    ["claer"]="clear"
    ["clera"]="clear"
    ["instol"]="install"
    ["instal"]="install"
    ["isntall"]="install"
    ["installl"]="install"
    # Romanian-English mixing
    ["sterge"]="rm"
    ["creaza"]="touch"
    ["folder"]="mkdir"
    ["copiaza"]="cp"
    ["muta"]="mv"
    ["cauta"]="find"
    ["editeaza"]="nvim"
    ["deschide"]="open"
    ["ruleaza"]="run"
    ["porneste"]="start"
    ["opreste"]="stop"
    ["actualizeaza"]="update"
    ["instaleaza"]="install"
    ["dezinstaleaza"]="uninstall"
    ["client"]="p4v"
    ["perforce"]="p4"
)

# Natural language command patterns
typeset -gA NLP_NATURAL_PATTERNS
NLP_NATURAL_PATTERNS=(
    # English patterns
    ["show files"]="ls -la"
    ["list files"]="ls -la"
    ["show hidden"]="ls -la"
    ["list all"]="ls -la"
    ["go to"]="cd"
    ["change to"]="cd"
    ["go home"]="cd ~"
    ["make folder"]="mkdir -p"
    ["create folder"]="mkdir -p"
    ["make directory"]="mkdir -p"
    ["create directory"]="mkdir -p"
    ["remove file"]="rm"
    ["delete file"]="rm"
    ["remove folder"]="rm -rf"
    ["delete folder"]="rm -rf"
    ["copy file"]="cp"
    ["move file"]="mv"
    ["find file"]="fd"
    ["search file"]="fd"
    ["find text"]="rg"
    ["search text"]="rg"
    ["edit file"]="nvim"
    ["open file"]="nvim"
    ["show content"]="cat"
    ["read file"]="cat"
    ["show disk"]="df -h"
    ["disk usage"]="df -h"
    ["disk space"]="df -h"
    ["free space"]="df -h"
    ["memory usage"]="free -h"
    ["ram usage"]="free -h"
    ["show memory"]="free -h"
    ["cpu usage"]="htop"
    ["system monitor"]="htop"
    ["process list"]="ps aux"
    ["running processes"]="ps aux"
    ["kill process"]="pkill"
    ["stop process"]="pkill"
    ["update system"]="yay -Syu"
    ["upgrade system"]="yay -Syu"
    ["install package"]="yay -S"
    ["remove package"]="yay -Rns"
    ["uninstall package"]="yay -Rns"
    ["search package"]="yay -Ss"
    ["clean cache"]="yay -Sc"
    ["clear cache"]="yay -Sc"
    ["clean orphans"]="yay -Rns \$(yay -Qtdq)"
    ["remove orphans"]="yay -Rns \$(yay -Qtdq)"
    ["my ip"]="curl -s ipinfo.io/ip"
    ["what is my ip"]="curl -s ipinfo.io/ip"
    ["ip address"]="ip addr show"
    ["network info"]="ip addr show"
    ["weather"]="curl wttr.in"
    ["git status"]="git status"
    ["git log"]="git log --oneline"
    ["git diff"]="git diff"
    ["git push"]="git push"
    ["git pull"]="git pull"
    ["git commit"]="git commit"
    ["restart"]="sudo systemctl restart"
    ["start service"]="sudo systemctl start"
    ["stop service"]="sudo systemctl stop"
    ["service status"]="systemctl status"
    # Romanian patterns
    ["arata fisiere"]="ls -la"
    ["listeaza fisiere"]="ls -la"
    ["arata ascunse"]="ls -la"
    ["du-te la"]="cd"
    ["mergi la"]="cd"
    ["creaza folder"]="mkdir -p"
    ["fa folder"]="mkdir -p"
    ["sterge fisier"]="rm"
    ["copiaza fisier"]="cp"
    ["muta fisier"]="mv"
    ["cauta fisier"]="fd"
    ["editeaza fisier"]="nvim"
    ["deschide fisier"]="nvim"
    ["arata continut"]="cat"
    ["citeste fisier"]="cat"
    ["spatiu disc"]="df -h"
    ["memorie folosita"]="free -h"
    ["actualizeaza sistem"]="yay -Syu"
    ["instaleaza pachet"]="yay -S"
    ["sterge pachet"]="yay -Rns"
    ["cauta pachet"]="yay -Ss"
    ["curata cache"]="yay -Sc"
    ["sterge orfani"]="yay -Rns \$(yay -Qtdq)"
    ["ce ip am"]="curl -s ipinfo.io/ip"
    ["adresa ip"]="ip addr show"
    ["vreme"]="curl wttr.in"
)

# Package name synonyms
typeset -gA NLP_PACKAGE_SYNONYMS
NLP_PACKAGE_SYNONYMS=(
    ["client perforce"]="p4v"
    ["perforce client"]="p4v"
    ["perforce gui"]="p4v"
    ["perforce tool"]="p4v"
    ["p4 client"]="p4v"
    ["p4 gui"]="p4v"
    ["youtube downloader"]="yt-dlp"
    ["youtube dl"]="yt-dlp"
    ["video downloader"]="yt-dlp"
    ["code editor"]="code"
    ["vscode"]="code"
    ["visual studio"]="code"
    ["text editor"]="nvim"
    ["vim"]="nvim"
    ["neovim"]="nvim"
    ["file manager"]="dolphin"
    ["music player"]="spotify"
    ["video player"]="vlc"
    ["browser"]="firefox"
    ["web browser"]="firefox"
    ["terminal"]="kitty"
    ["image editor"]="gimp"
    ["photo editor"]="gimp"
    ["pdf viewer"]="okular"
    ["pdf reader"]="okular"
    ["archive manager"]="ark"
    ["zip tool"]="ark"
    ["git gui"]="lazygit"
    ["git client"]="lazygit"
    ["docker gui"]="lazydocker"
    ["system monitor"]="btop"
    ["task manager"]="btop"
    ["network analyzer"]="wireshark"
    ["packet sniffer"]="wireshark"
)

# Calculate Levenshtein distance for typo detection
levenshtein_distance() {
    local s1="$1"
    local s2="$2"
    local len1=${#s1}
    local len2=${#s2}

    # Simple implementation
    if [[ $len1 -eq 0 ]]; then
        echo $len2
        return
    fi
    if [[ $len2 -eq 0 ]]; then
        echo $len1
        return
    fi

    local -a matrix

    for ((i=0; i<=len1; i++)); do
        matrix[$i,0]=$i
    done
    for ((j=0; j<=len2; j++)); do
        matrix[0,$j]=$j
    done

    for ((i=1; i<=len1; i++)); do
        for ((j=1; j<=len2; j++)); do
            local cost=0
            [[ "${s1:$((i-1)):1}" != "${s2:$((j-1)):1}" ]] && cost=1

            local delete=$((matrix[$((i-1)),$j] + 1))
            local insert=$((matrix[$i,$((j-1))] + 1))
            local substitute=$((matrix[$((i-1)),$((j-1))] + cost))

            local min=$delete
            [[ $insert -lt $min ]] && min=$insert
            [[ $substitute -lt $min ]] && min=$substitute

            matrix[$i,$j]=$min
        done
    done

    echo ${matrix[$len1,$len2]}
}

# Find closest command match
find_closest_command() {
    local input="$1"
    local max_distance=3
    local best_match=""
    local best_distance=999

    # Check typo map first
    if [[ -n "${NLP_TYPO_MAP[$input]}" ]]; then
        echo "${NLP_TYPO_MAP[$input]}"
        return 0
    fi

    # Check installed commands
    local -a commands=($(compgen -c 2>/dev/null | sort -u | head -500))

    for cmd in "${commands[@]}"; do
        local dist=$(levenshtein_distance "$input" "$cmd")
        if [[ $dist -lt $best_distance ]] && [[ $dist -le $max_distance ]]; then
            best_distance=$dist
            best_match="$cmd"
        fi
    done

    echo "$best_match"
}

# Parse natural language input
parse_natural_language() {
    local input="$1"
    local input_lower="${input:l}"

    # Check for exact natural language patterns
    for pattern in "${(@k)NLP_NATURAL_PATTERNS}"; do
        if [[ "$input_lower" == *"$pattern"* ]]; then
            echo "${NLP_NATURAL_PATTERNS[$pattern]}"
            return 0
        fi
    done

    # Check for package synonyms
    for synonym in "${(@k)NLP_PACKAGE_SYNONYMS}"; do
        if [[ "$input_lower" == *"$synonym"* ]]; then
            echo "yay -S ${NLP_PACKAGE_SYNONYMS[$synonym]}"
            return 0
        fi
    done

    return 1
}

# NLP suggestion interface
show_nlp_suggestion() {
    local original="$1"
    local suggestion="$2"
    local alternatives=("${@:3}")

    printf "\n"
    printf "  %b╭─────────────────────────────────────────────────────────────╮%b\n" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    printf "  %b│%b  %b🤖 NLP ASSISTANT%b                                          %b│%b\n" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[magenta]}${CYBER_STYLE[bold]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    printf "  %b├─────────────────────────────────────────────────────────────┤%b\n" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    printf "  %b│%b  Ai vrut să spui:                                          %b│%b\n" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    printf "  %b│%b    %b%s%b                                     %b│%b\n" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[green]}${CYBER_STYLE[bold]}" "$suggestion" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    printf "  %b├─────────────────────────────────────────────────────────────┤%b\n" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    printf "  %b│%b  %b[Enter]%b Da  •  %b[Tab]%b Vezi alternative  •  %b[Esc]%b Nu       %b│%b\n" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    printf "  %b╰─────────────────────────────────────────────────────────────╯%b\n" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"

    # Handle user input
    local key
    read -sk1 key

    case "$key" in
        $'\n')  # Enter - accept suggestion
            BUFFER="$suggestion"
            zle accept-line
            return 0
            ;;
        $'\t')  # Tab - show alternatives
            if [[ ${#alternatives[@]} -gt 0 ]]; then
                printf "\n  %b Alternative:%b\n" "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
                local i=1
                for alt in "${alternatives[@]}"; do
                    printf "    %b%d)%b %s\n" "${CYBER_COLORS[yellow]}" "$i" "${CYBER_STYLE[reset]}" "$alt"
                    ((i++))
                done
            fi
            ;;
        $'\e')  # Escape - cancel
            return 1
            ;;
    esac
}

# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
# SECTION 18: FEATURE 7 - INTENT ENGINE
# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550

# Intent patterns
typeset -gA INTENT_PATTERNS
INTENT_PATTERNS=(
    ["vreau un server"]="server"
    ["porneste server"]="server"
    ["start server"]="server"
    ["local server"]="server"
    ["server local"]="server"
    ["descarca video"]="download_video"
    ["download video"]="download_video"
    ["youtube download"]="download_video"
    ["descarca yt"]="download_video"
    ["descarca de pe youtube"]="download_video"
    ["curata cache"]="cleanup"
    ["curata sistem"]="cleanup"
    ["sterge cache"]="cleanup"
    ["sterge orphan"]="cleanup"
    ["clean system"]="cleanup"
    ["cleanup"]="cleanup"
    ["cur\u0103\u021b\u0103"]="cleanup"
    ["actualizeaza tot"]="full_update"
    ["update all"]="full_update"
    ["update everything"]="full_update"
    ["full update"]="full_update"
    ["instaleaza"]="install"
    ["install"]="install"
    ["pune"]="install"
    ["vreau sa instalez"]="install"
    ["fa backup"]="backup"
    ["backup"]="backup"
    ["salveaza"]="backup"
    ["creeaza backup"]="backup"
    ["verifica sistem"]="system_check"
    ["system check"]="system_check"
    ["check system"]="system_check"
    ["diagnoza"]="system_check"
    ["gaseste fisiere mari"]="find_large"
    ["find large files"]="find_large"
    ["ce ocupa spatiu"]="find_large"
    ["spatiu ocupat"]="find_large"
    ["conecteaza la"]="connect"
    ["connect to"]="connect"
    ["ssh to"]="connect"
    ["remote"]="connect"
    ["deschide proiect"]="open_project"
    ["open project"]="open_project"
    ["go to project"]="open_project"
    ["lucreaza la"]="open_project"
    ["git setup"]="git_setup"
    ["setup git"]="git_setup"
    ["initializeaza git"]="git_setup"
    ["git init project"]="git_setup"
)

# Intent handlers
handle_intent_server() {
    local port=${1:-8000}
    local type=${2:-python}

    local commands=()
    local explanation=""

    case "$type" in
        python|py)
            commands+=("python -m http.server $port")
            explanation="Server Python HTTP pe portul $port"
            ;;
        php)
            commands+=("php -S localhost:$port")
            explanation="Server PHP pe portul $port"
            ;;
        node)
            commands+=("npx http-server -p $port")
            explanation="Server Node.js pe portul $port"
            ;;
        *)
            commands+=("python -m http.server $port")
            explanation="Server HTTP rapid pe portul $port"
            ;;
    esac

    show_intent_confirmation "Server Local" "$explanation" "${commands[@]}"
}

handle_intent_download_video() {
    local url="$1"
    local quality=${2:-best}

    local commands=()
    local explanation=""

    if [[ -z "$url" ]]; then
        printf "%b\u2753 Introdu URL-ul video-ului:%b " "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
        read url
    fi

    case "$quality" in
        4k|2160)
            commands+=("yt-dlp -f 'bestvideo[height<=2160]+bestaudio/best[height<=2160]' --merge-output-format mp4 '$url'")
            explanation="Descarc\u0103 video 4K cu cea mai bun\u0103 calitate audio"
            ;;
        1080|hd|fullhd)
            commands+=("yt-dlp -f 'bestvideo[height<=1080]+bestaudio/best[height<=1080]' --merge-output-format mp4 '$url'")
            explanation="Descarc\u0103 video 1080p cu cea mai bun\u0103 calitate audio"
            ;;
        audio|mp3)
            commands+=("yt-dlp -x --audio-format mp3 --audio-quality 0 '$url'")
            explanation="Extrage doar audio \u00een format MP3"
            ;;
        *)
            commands+=("yt-dlp -f 'bestvideo+bestaudio/best' --merge-output-format mp4 '$url'")
            explanation="Descarc\u0103 video la cea mai bun\u0103 calitate disponibil\u0103"
            ;;
    esac

    show_intent_confirmation "Download Video" "$explanation" "${commands[@]}"
}

handle_intent_cleanup() {
    local commands=(
        "sudo pacman -Sc --noconfirm"
        "yay -Rns \$(yay -Qtdq) 2>/dev/null || echo 'No orphans found'"
        "rm -rf ~/.cache/*"
        "sudo journalctl --vacuum-time=7d"
    )
    local explanation="Cur\u0103\u021b\u0103 cache-ul pachetelor, elimin\u0103 pachete orfane, \u0219terge cache-ul utilizator \u0219i cur\u0103\u021b\u0103 log-uri vechi"

    show_intent_confirmation "Cur\u0103\u021bare Sistem" "$explanation" "${commands[@]}"
}

handle_intent_full_update() {
    local commands=(
        "yay -Syu --noconfirm"
        "flatpak update -y 2>/dev/null || true"
        "rustup update 2>/dev/null || true"
        "npm update -g 2>/dev/null || true"
    )
    local explanation="Actualizeaz\u0103: pachete sistem (yay), Flatpak, Rust, \u0219i pachete npm globale"

    show_intent_confirmation "Actualizare Complet\u0103" "$explanation" "${commands[@]}"
}

handle_intent_install() {
    local package="$1"

    if [[ -z "$package" ]]; then
        printf "%b\u2753 Ce dore\u0219ti s\u0103 instalezi:%b " "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
        read package
    fi

    # Check for package synonyms
    local resolved_package="$package"
    for synonym in "${(@k)NLP_PACKAGE_SYNONYMS}"; do
        if [[ "${package:l}" == *"$synonym"* ]]; then
            resolved_package="${NLP_PACKAGE_SYNONYMS[$synonym]}"
            break
        fi
    done

    local commands=("yay -S $resolved_package")
    local explanation="Instaleaz\u0103 pachetul '$resolved_package' folosind yay (AUR + repos oficiale)"

    show_intent_confirmation "Instalare" "$explanation" "${commands[@]}"
}

handle_intent_backup() {
    local target=${1:-$HOME}
    local dest=${2:-$HOME/backups}
    local timestamp=$(date +%Y%m%d_%H%M%S)

    mkdir -p "$dest"

    local commands=(
        "tar -czvf '$dest/backup_$timestamp.tar.gz' --exclude='.cache' --exclude='node_modules' --exclude='.local/share/Trash' '$target'"
    )
    local explanation="Creaz\u0103 arhiv\u0103 backup a '$target' \u00een '$dest/backup_$timestamp.tar.gz'"

    show_intent_confirmation "Backup" "$explanation" "${commands[@]}"
}

handle_intent_system_check() {
    local commands=(
        "echo '=== Spa\u021biu Disc ===' && df -h"
        "echo '=== Memorie ===' && free -h"
        "echo '=== Procese CPU ===' && ps aux --sort=-%cpu | head -5"
        "echo '=== Servicii Failed ===' && systemctl --failed"
        "echo '=== Erori Recente ===' && journalctl -p err -n 10"
    )
    local explanation="Verific\u0103: spa\u021biu disc, memorie, top procese CPU, servicii failed, \u0219i erori recente"

    show_intent_confirmation "Verificare Sistem" "$explanation" "${commands[@]}"
}

handle_intent_find_large() {
    local path=${1:-.}
    local limit=${2:-10}

    local commands=(
        "du -ah '$path' 2>/dev/null | sort -rh | head -n $limit"
    )
    local explanation="G\u0103se\u0219te cele mai mari $limit fi\u0219iere/foldere \u00een '$path'"

    show_intent_confirmation "Fi\u0219iere Mari" "$explanation" "${commands[@]}"
}

handle_intent_connect() {
    local target="$1"

    if [[ -z "$target" ]]; then
        printf "%b\u2753 Unde dore\u0219ti s\u0103 te conectezi (user@host):%b " "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
        read target
    fi

    local commands=("ssh $target")
    local explanation="Conectare SSH la '$target'"

    show_intent_confirmation "Conexiune SSH" "$explanation" "${commands[@]}"
}

handle_intent_open_project() {
    local project="$1"

    # Search in common project directories
    local project_dirs=(
        "$HOME/projects"
        "$HOME/dev"
        "$HOME/work"
        "$HOME/code"
        "$HOME/repos"
        "$HOME/git"
    )

    local found_path=""
    for dir in "${project_dirs[@]}"; do
        if [[ -d "$dir/$project" ]]; then
            found_path="$dir/$project"
            break
        fi
    done

    if [[ -n "$found_path" ]]; then
        local commands=(
            "cd '$found_path'"
            "ls -la"
        )
        local explanation="Deschide proiectul '$project' din '$found_path'"
        show_intent_confirmation "Deschide Proiect" "$explanation" "${commands[@]}"
    else
        printf "%b\u274c Proiect '%s' neg\u0103sit \u00een directoarele standard%b\n" \
            "${CYBER_COLORS[red]}" "$project" "${CYBER_STYLE[reset]}"
    fi
}

handle_intent_git_setup() {
    local name="$1"

    if [[ -z "$name" ]]; then
        printf "%b\u2753 Numele proiectului:%b " "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
        read name
    fi

    local commands=(
        "mkdir -p $name && cd $name"
        "git init"
        "echo '# $name' > README.md"
        "echo '.env' > .gitignore"
        "echo 'node_modules/' >> .gitignore"
        "echo '__pycache__/' >> .gitignore"
        "git add ."
        "git commit -m 'Initial commit'"
    )
    local explanation="Ini\u021bializeaz\u0103 repository Git nou cu README \u0219i .gitignore standard"

    show_intent_confirmation "Setup Git" "$explanation" "${commands[@]}"
}

# Intent confirmation UI
show_intent_confirmation() {
    local title="$1"
    local explanation="$2"
    shift 2
    local commands=("$@")

    printf "\n"
    printf "  %b╔════════════════════════════════════════════════════════════════════╗%b\n" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    printf "  %b║%b  %b🎯 INTENT: %s%b                                     %b║%b\n" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[magenta]}${CYBER_STYLE[bold]}" "$title" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    printf "  %b╠════════════════════════════════════════════════════════════════════╣%b\n" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    printf "  %b║%b  %s  %b║%b\n" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}" \
        "$explanation" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    printf "  %b╠════════════════════════════════════════════════════════════════════╣%b\n" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    printf "  %b║%b  %bComenzi care vor rula:%b                                         %b║%b\n" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"

    for cmd in "${commands[@]}"; do
        printf "  %b║%b    %b→%b %s  %b║%b\n" \
            "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}" \
            "${CYBER_COLORS[green]}" "${CYBER_STYLE[reset]}" \
            "$cmd" \
            "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    done

    printf "  %b╠════════════════════════════════════════════════════════════════════╣%b\n" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    printf "  %b║%b  %b[Enter]%b Execută  •  %b[e]%b Editează  •  %b[Esc]%b Anulează            %b║%b\n" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    printf "  %b╚════════════════════════════════════════════════════════════════════╝%b\n" \
        "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"

    local key
    read -sk1 key

    case "$key" in
        $'\n')  # Enter - execute
            printf "\n%b\u26a1 Executing...%b\n\n" "${CYBER_COLORS[green]}" "${CYBER_STYLE[reset]}"
            for cmd in "${commands[@]}"; do
                eval "$cmd"
            done
            return 0
            ;;
        e|E)  # Edit
            printf "\n%b\ud83d\udcdd Editeaz\u0103 comanda:%b\n" "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
            BUFFER="${commands[*]}"
            zle redisplay
            ;;
        $'\e')  # Escape - cancel
            printf "\n%b\u274c Anulat%b\n" "${CYBER_COLORS[red]}" "${CYBER_STYLE[reset]}"
            return 1
            ;;
    esac
}

# Main intent parser
parse_intent() {
    local input="$1"
    local input_lower="${input:l}"

    for pattern in "${(@k)INTENT_PATTERNS}"; do
        if [[ "$input_lower" == *"$pattern"* ]]; then
            local intent="${INTENT_PATTERNS[$pattern]}"
            local args="${input_lower#*$pattern}"
            args="${args## }"  # Trim leading space

            case "$intent" in
                server)         handle_intent_server "$args" ;;
                download_video) handle_intent_download_video "$args" ;;
                cleanup)        handle_intent_cleanup ;;
                full_update)    handle_intent_full_update ;;
                install)        handle_intent_install "$args" ;;
                backup)         handle_intent_backup "$args" ;;
                system_check)   handle_intent_system_check ;;
                find_large)     handle_intent_find_large "$args" ;;
                connect)        handle_intent_connect "$args" ;;
                open_project)   handle_intent_open_project "$args" ;;
                git_setup)      handle_intent_git_setup "$args" ;;
            esac
            return 0
        fi
    done

    return 1
}

# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
# SECTION 19: FEATURE 8 - COMMAND DOCTOR
# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550

# Error patterns and fixes
typeset -gA COMMAND_DOCTOR_PATTERNS
COMMAND_DOCTOR_PATTERNS=(
    # Permission errors
    ["Permission denied"]="permission"
    ["Operation not permitted"]="permission"
    ["cannot open"]="permission"
    ["access denied"]="permission"
    # Package not found
    ["package not found"]="package_not_found"
    ["target not found"]="package_not_found"
    ["No package"]="package_not_found"
    ["Unable to locate package"]="package_not_found"
    # Command not found
    ["command not found"]="command_not_found"
    ["not found"]="command_not_found"
    # File/Directory errors
    ["No such file or directory"]="file_not_found"
    ["Is a directory"]="is_directory"
    ["Not a directory"]="not_directory"
    ["File exists"]="file_exists"
    ["Directory not empty"]="dir_not_empty"
    # Git errors
    ["fatal: not a git repository"]="not_git_repo"
    ["nothing to commit"]="nothing_to_commit"
    ["merge conflict"]="merge_conflict"
    ["Your branch is behind"]="branch_behind"
    ["Your branch is ahead"]="branch_ahead"
    # Network errors
    ["Could not resolve host"]="dns_error"
    ["Connection refused"]="connection_refused"
    ["Connection timed out"]="connection_timeout"
    ["Network is unreachable"]="network_unreachable"
    # Disk errors
    ["No space left on device"]="disk_full"
    ["Disk quota exceeded"]="disk_quota"
    # Memory errors
    ["Cannot allocate memory"]="out_of_memory"
    ["Killed"]="oom_killed"
    # Process errors
    ["Address already in use"]="port_in_use"
    ["Resource temporarily unavailable"]="resource_busy"
)


typeset -g CYBER_DOCTOR_ENABLED=1
typeset -g CYBER_DOCTOR_LAST_HASH=""

generate_fix_suggestions() {
    local error_type="$1" error_output="$2" command="$3"
    local -a suggestions=()

    local base_cmd="${command%% *}"

    case "$error_type" in
        permission)
            suggestions+=("sudo $command")
            suggestions+=("chmod +x <file>")
            suggestions+=("chown $USER:$USER <file>")
            ;;

        package_not_found)
            local pkg=""
            pkg="$(printf '%s\n' "$error_output" | command grep -oE '(target not found:|package not found:)[[:space:]]*[^[:space:]]+' | command awk '{print $NF}' | command head -n1 2>/dev/null)"
            [[ -n "$pkg" ]] && suggestions+=("yay -Ss $pkg")
            suggestions+=("pacman -Fy && pacman -F $base_cmd")
            ;;

        command_not_found)
            local similar=""
            similar="$(find_closest_command "$base_cmd" 2>/dev/null)"
            [[ -n "$similar" ]] && suggestions+=("$similar")
            suggestions+=("pacman -F $base_cmd")
            suggestions+=("yay -Ss $base_cmd")
            ;;

        file_not_found)
            suggestions+=("touch <file>")
            suggestions+=("mkdir -p <dir>")
            suggestions+=("find . -name 'pattern'")
            ;;

        not_git_repo)
            suggestions+=("git init")
            suggestions+=("cd <git-directory>")
            ;;

        merge_conflict)
            suggestions+=("git status")
            suggestions+=("git mergetool")
            ;;

        disk_full)
            suggestions+=("df -h")
            suggestions+=("sudo pacman -Sc")
            suggestions+=("du -sh ~/.cache/* | sort -rh | head")
            ;;

        port_in_use)
            local port=""
            port="$(printf '%s\n' "$error_output" | command grep -oE '[0-9]{2,5}' | command head -n1 2>/dev/null)"
            [[ -n "$port" ]] && suggestions+=("lsof -i :$port")
            [[ -n "$port" ]] && suggestions+=("kill \$(lsof -t -i:$port)")
            ;;

        dns_error|connection_refused|connection_timeout|network_unreachable)
            suggestions+=("ping -c 1 1.1.1.1")
            suggestions+=("ping -c 1 google.com")
            command -v nmcli >/dev/null 2>&1 && suggestions+=("nmcli dev status")
            ;;

        *)
            suggestions+=("Uită-te la stderr (tail) de mai jos")
            suggestions+=("Rulează din nou cu -v / --verbose dacă există")
            ;;
    esac

    printf '%s\n' "${suggestions[@]}"
}

show_command_doctor() {
    local exit_code=$1 command="$2" error_output="$3"

    (( CYBER_DOCTOR_ENABLED == 1 )) || return
    [[ $exit_code -eq 0 ]] && return
    [[ -z "$error_output" ]] && return

    # anti-spam: același cmd+stderr => nu repetăm
    local key="${exit_code}|${command}|${error_output}"
    local hash=""
    hash="$(printf '%s' "$key" | command sha1sum 2>/dev/null | command awk '{print $1}')"
    [[ -n "$hash" && "$hash" == "$CYBER_DOCTOR_LAST_HASH" ]] && return
    [[ -n "$hash" ]] && CYBER_DOCTOR_LAST_HASH="$hash"

    local error_type=""
    for pattern in "${(@k)COMMAND_DOCTOR_PATTERNS}"; do
        [[ "$error_output" == "$pattern" ]] && { error_type="${COMMAND_DOCTOR_PATTERNS[$pattern]}"; break; }
    done
    [[ -z "$error_type" ]] && error_type="unknown"

    local -a suggestions
    suggestions=("${(@f)$(generate_fix_suggestions "$error_type" "$error_output" "$command")}")

    local -a err_tail
    if command -v tail >/dev/null 2>&1; then
        err_tail=("${(@f)$(printf '%s\n' "$error_output" | command tail -n 8)}")
    else
        err_tail=("${(@f)$(printf '%s\n' "$error_output")}")
    fi

    printf "\n  %b╭─ 🩺 COMMAND DOCTOR ─────────────────────────────────────────╮%b\n" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}"
    printf "  %b│%b Exit code: %b%d%b   Tip: %b%s%b\n" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}" "${CYBER_COLORS[red]}" "$exit_code" "${CYBER_STYLE[reset]}" "${CYBER_COLORS[cyan]}" "$error_type" "${CYBER_STYLE[reset]}"
    printf "  %b├───────────────────────────────────────────────────────────────┤%b\n" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}"
    printf "  %b│%b Sugestii:%b\n" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}" "${CYBER_STYLE[reset]}"

    local i=1
    local s
    for s in "${suggestions[@]}"; do
        [[ -n "$s" ]] && printf "  %b│%b  %b[%d]%b %s\n" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}" "${CYBER_COLORS[green]}" "$i" "${CYBER_STYLE[reset]}" "$s"
        ((i++))
    done

    printf "  %b├───────────────────────────────────────────────────────────────┤%b\n" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}"
    printf "  %b│%b stderr (tail):%b\n" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}" "${CYBER_STYLE[reset]}"
    for s in "${err_tail[@]}"; do
        [[ -n "$s" ]] && printf "  %b│%b  %s\n" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}" "$s"
    done

    printf "  %b╰───────────────────────────────────────────────────────────────╯%b\n" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}"
}

# FEATURE 9: CLIPBOARD BAR
typeset -ga CYBER_CLIPBOARD_RING=()
typeset -g CYBER_CLIPBOARD_MAX=10
typeset -g CLIPBOARD_BAR_VISIBLE=0
clipboard_add() {
    local item="$1"
    [[ -z "$item" ]] && return
    CYBER_CLIPBOARD_RING=("$item" "${CYBER_CLIPBOARD_RING[@]}")
    [[ ${#CYBER_CLIPBOARD_RING[@]} -gt $CYBER_CLIPBOARD_MAX ]] && CYBER_CLIPBOARD_RING=("${CYBER_CLIPBOARD_RING[@]:0:$CYBER_CLIPBOARD_MAX}")
    printf '%s\n' "${CYBER_CLIPBOARD_RING[@]}" > "$CYBER_DATA_DIR/clipboard/ring.txt"
}
clipboard_load() {
    [[ -f "$CYBER_DATA_DIR/clipboard/ring.txt" ]] && {
        CYBER_CLIPBOARD_RING=()
        while IFS= read -r line; do CYBER_CLIPBOARD_RING+=("$line"); done < "$CYBER_DATA_DIR/clipboard/ring.txt"
    }
}
render_clipboard_bar() {
    [[ $CLIPBOARD_BAR_VISIBLE -eq 0 ]] && return
    printf "\n%b┌─ 📋 CLIPBOARD ─────────────────────────────────────────────────┐%b\n" "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    local i=1
    for item in "${CYBER_CLIPBOARD_RING[@]:0:5}"; do
        local display="${item:0:50}"
        [[ ${#item} -gt 50 ]] && display="${display}..."
        printf "%b│%b [%d] %s\n" "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}" "$i" "$display"
        ((i++))
    done
    printf "%b└───────────────────────────────────────────────────────────────────┘%b\n" "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
}
toggle_clipboard_bar() { ((CLIPBOARD_BAR_VISIBLE = !CLIPBOARD_BAR_VISIBLE)); render_clipboard_bar; zle redisplay; }
zle -N toggle_clipboard_bar
clip() {
    case "$1" in
        add) shift; clipboard_add "$*" ;;
        list) render_clipboard_bar ;;
        get) [[ -n "${CYBER_CLIPBOARD_RING[$2]}" ]] && printf '%s' "${CYBER_CLIPBOARD_RING[$2]}" | xclip -selection clipboard && echo "Copied #$2" ;;
        clear) CYBER_CLIPBOARD_RING=(); rm -f "$CYBER_DATA_DIR/clipboard/ring.txt"; echo "Clipboard cleared" ;;
        *) echo "Usage: clip <add|list|get|clear> [args]" ;;
    esac
}

# FEATURE 10: INLINE IMAGE (Kitty protocol)
display_image_inline() {
    local file="$1" width="${2:-auto}" height="${3:-auto}"
    [[ ! -f "$file" ]] && { echo "File not found: $file"; return 1; }
    if [[ "$TERM" == *"kitty"* ]] || [[ -n "$KITTY_WINDOW_ID" ]]; then
        kitty +kitten icat --align=left "$file"
    elif command -v chafa &>/dev/null; then
        chafa --size=80x40 "$file"
    elif command -v catimg &>/dev/null; then
        catimg -w 80 "$file"
    else
        echo "No image viewer available. Install kitty, chafa, or catimg."
    fi
}
img() { display_image_inline "$@"; }

# FEATURE 11: MINI FILE EXPLORER
typeset -g FILE_EXPLORER_DIR="$PWD"
typeset -g FILE_EXPLORER_SELECTED=1
typeset -ga FILE_EXPLORER_ITEMS=()
file_explorer_load() {
    FILE_EXPLORER_ITEMS=()
    [[ "$FILE_EXPLORER_DIR" != "/" ]] && FILE_EXPLORER_ITEMS+=("..")
    while IFS= read -r item; do FILE_EXPLORER_ITEMS+=("$item"); done < <(ls -1A "$FILE_EXPLORER_DIR" 2>/dev/null | head -20)
}
get_file_icon() {
    local name="$1" path="$FILE_EXPLORER_DIR/$name"
    [[ -d "$path" ]] && { echo "📁"; return; }
    case "${name##*.}" in
        sh|zsh|bash) echo "🔧" ;; py) echo "🐍" ;; js|ts) echo "📜" ;; c|cpp|h) echo "⚙️" ;;
        md|txt) echo "📄" ;; json|yaml|yml) echo "📋" ;; jpg|jpeg|png|gif|svg) echo "🖼️" ;;
        mp3|wav|flac) echo "🎵" ;; mp4|mkv|avi) echo "🎬" ;; zip|tar|gz|7z) echo "📦" ;;
        *) echo "📄" ;;
    esac
}
render_file_explorer() {
    clear
    printf "%b┌─ 📂 %s ─────────────────────────────────────────────────┐%b\n" "${CYBER_COLORS[cyan]}" "${FILE_EXPLORER_DIR}" "${CYBER_STYLE[reset]}"
    local i=1
    for item in "${FILE_EXPLORER_ITEMS[@]}"; do
        local icon=$(get_file_icon "$item")
        if [[ $i -eq $FILE_EXPLORER_SELECTED ]]; then
            printf "%b│ ▶ %s %s%b\n" "${CYBER_COLORS[green]}${CYBER_STYLE[bold]}" "$icon" "$item" "${CYBER_STYLE[reset]}"
        else
            printf "%b│   %s %s%b\n" "${CYBER_COLORS[white]}" "$icon" "$item" "${CYBER_STYLE[reset]}"
        fi
        ((i++))
    done
    printf "%b└─ [↑↓] Navigate [Enter] Open [i] Insert [q] Quit ─────────────────┘%b\n" "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
}
file_explorer() {
    FILE_EXPLORER_DIR="$PWD"
    FILE_EXPLORER_SELECTED=1
    file_explorer_load
    while true; do
        render_file_explorer
        read -sk1 key
        case "$key" in
            $'\e') read -sk2 seq
                case "$seq" in
                    '[A') ((FILE_EXPLORER_SELECTED > 1)) && ((FILE_EXPLORER_SELECTED--)) ;;
                    '[B') ((FILE_EXPLORER_SELECTED < ${#FILE_EXPLORER_ITEMS[@]})) && ((FILE_EXPLORER_SELECTED++)) ;;
                esac ;;
            '') local selected="${FILE_EXPLORER_ITEMS[$FILE_EXPLORER_SELECTED]}"
                local path="$FILE_EXPLORER_DIR/$selected"
                if [[ -d "$path" ]]; then
                    FILE_EXPLORER_DIR="$(cd "$path" && pwd)"
                    FILE_EXPLORER_SELECTED=1
                    file_explorer_load
                else
                    ${EDITOR:-nvim} "$path"
                fi ;;
            i) local selected="${FILE_EXPLORER_ITEMS[$FILE_EXPLORER_SELECTED]}"
               BUFFER="$FILE_EXPLORER_DIR/$selected"
               clear; zle redisplay 2>/dev/null; return ;;
            q) clear; return ;;
        esac
    done
}
file_explorer_widget() { file_explorer; }
zle -N file_explorer_widget
alias fe='file_explorer'

# FEATURE 12: MINI SEARCH ENGINE
cyber_search() {
  local query="$*"
  [[ -z "$query" ]] && { echo "Usage: ? <query>"; return 1; }

  local choice
  echo
  echo "Search: $query"
  echo "  1) man   2) tldr   3) apropos   4) web"
  echo -n "Choose: "
  read -rk1 choice
  echo

  case "$choice" in
    1)
      man "$query"
      ;;
    2)
      if command -v tldr >/dev/null 2>&1; then
        if command -v bat >/dev/null 2>&1; then
          tldr "$query" 2>/dev/null | bat -l md -p 2>/dev/null || tldr "$query" 2>/dev/null
        else
          tldr "$query" 2>/dev/null
        fi
      else
        echo "tldr not installed"
      fi
      ;;
    3)
      apropos "$query" 2>/dev/null || echo "No apropos results for $query"
      ;;
    4)
      # fallback simplu dacă nu ai “internet engine”:
      local q="${query// /+}"
      command -v xdg-open >/dev/null 2>&1 && xdg-open "https://duckduckgo.com/?q=$q" >/dev/null 2>&1 &
      ;;
    *)
      echo "Cancelled"
      ;;
  esac
}
alias '?'='cyber_search'

# FEATURE 13: SMART AUTOCOMPLETE
typeset -gA COMMAND_FREQUENCY
load_command_frequency() { [[ -f "$CYBER_DATA_DIR/history/frequency.txt" ]] && while IFS=: read -r cmd count; do COMMAND_FREQUENCY[$cmd]=$count; done < "$CYBER_DATA_DIR/history/frequency.txt"; }
save_command_frequency() { for cmd in "${(@k)COMMAND_FREQUENCY}"; do printf '%s:%s\n' "$cmd" "${COMMAND_FREQUENCY[$cmd]}"; done > "$CYBER_DATA_DIR/history/frequency.txt"; }
update_command_frequency() {
    local cmd="${1%% *}"
    COMMAND_FREQUENCY[$cmd]=$((${COMMAND_FREQUENCY[$cmd]:-0} + 1))
}
get_smart_completions() {
    local prefix="$1"
    local -a results=()
    for cmd in "${(@k)COMMAND_FREQUENCY}"; do
        [[ "$cmd" == "$prefix"* ]] && results+=("${COMMAND_FREQUENCY[$cmd]}:$cmd")
    done
    printf '%s\n' "${results[@]}" | sort -t: -k1 -rn | cut -d: -f2 | head -5
}

# FEATURE 14: PREDICT NEXT COMMAND
typeset -gA COMMAND_SEQUENCES
load_command_sequences() { [[ -f "$CYBER_DATA_DIR/history/sequences.txt" ]] && while IFS=: read -r seq next count; do COMMAND_SEQUENCES["$seq"]="$next:$count"; done < "$CYBER_DATA_DIR/history/sequences.txt"; }
save_command_sequences() { for seq in "${(@k)COMMAND_SEQUENCES}"; do printf '%s:%s\n' "$seq" "${COMMAND_SEQUENCES[$seq]}"; done > "$CYBER_DATA_DIR/history/sequences.txt"; }
record_command_sequence() {
    local cmd="$1"
    [[ -n "$CYBER_LAST_COMMAND" ]] && {
        local key="$CYBER_LAST_COMMAND"
        local existing="${COMMAND_SEQUENCES[$key]}"
        if [[ -n "$existing" ]]; then
            local old_next="${existing%%:*}" old_count="${existing##*:}"
            [[ "$old_next" == "$cmd" ]] && COMMAND_SEQUENCES[$key]="$cmd:$((old_count + 1))" || COMMAND_SEQUENCES[$key]="$cmd:1"
        else
            COMMAND_SEQUENCES[$key]="$cmd:1"
        fi
    }
}
predict_next_command() {
    local last="${CYBER_LAST_COMMAND%% *}"
    [[ -z "$last" ]] && return
    local prediction="${COMMAND_SEQUENCES[$last]}"
    [[ -n "$prediction" ]] && {
        local next="${prediction%%:*}" count="${prediction##*:}"
        [[ $count -gt 2 ]] && printf "%bð¡ Next: %s%b\n" "${CYBER_COLORS[gray]}" "$next" "${CYBER_STYLE[reset]}"
    }
}

# FEATURE 15: MACROS
typeset -g MACRO_DIR="$CYBER_DATA_DIR/macros"
typeset -g CYBER_RECORDING_MACRO=0
typeset -g CYBER_CURRENT_MACRO=""
typeset -ga CYBER_MACRO_COMMANDS=()
typeset -g CYBER_MACRO_START_TIME=0
macro_record_start() {
    local name="${1:-macro_$(date +%s)}"
    CYBER_RECORDING_MACRO=1
    CYBER_CURRENT_MACRO="$name"
    CYBER_MACRO_COMMANDS=()
    CYBER_MACRO_START_TIME=$(date +%s)
    printf "%b🔴 Recording: %s (Ctrl+Shift+R to stop)%b\n" "${CYBER_COLORS[red]}" "$name" "${CYBER_STYLE[reset]}"
}
macro_record_stop() {
    [[ $CYBER_RECORDING_MACRO -eq 0 ]] && { echo "Not recording"; return; }
    CYBER_RECORDING_MACRO=0
    local duration=$(($(date +%s) - CYBER_MACRO_START_TIME))
    printf '# Macro: %s\n# Commands: %d\n' "$CYBER_CURRENT_MACRO" "${#CYBER_MACRO_COMMANDS[@]}" > "$MACRO_DIR/${CYBER_CURRENT_MACRO}.macro"
    printf '%s\n' "${CYBER_MACRO_COMMANDS[@]}" >> "$MACRO_DIR/${CYBER_CURRENT_MACRO}.macro"
    printf "%b✅ Saved: %s (%d commands)%b\n" "${CYBER_COLORS[green]}" "$CYBER_CURRENT_MACRO" "${#CYBER_MACRO_COMMANDS[@]}" "${CYBER_STYLE[reset]}"
    CYBER_CURRENT_MACRO="" CYBER_MACRO_COMMANDS=()
}
macro_add_command() { CYBER_MACRO_COMMANDS+=("$1"); }
macro_play() {
    local name="$1" file="$MACRO_DIR/${name}.macro"
    [[ ! -f "$file" ]] && { echo "Macro not found: $name"; return 1; }
    printf "%b▶️ Playing: %s%b\n" "${CYBER_COLORS[green]}" "$name" "${CYBER_STYLE[reset]}"
    while IFS= read -r line; do
        [[ "$line" == \#* ]] && continue
        [[ -z "$line" ]] && continue
        printf "%b> %s%b\n" "${CYBER_COLORS[cyan]}" "$line" "${CYBER_STYLE[reset]}"
        eval "$line"
    done < "$file"
}
macro_list() {
    printf "%b📼 Macros:%b\n" "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    for f in "$MACRO_DIR"/*.macro(N); do
        [[ -f "$f" ]] && printf "  → %s\n" "$(basename "$f" .macro)"
    done
}
macro() {
    case "${1:-list}" in
        record|rec|r) shift; macro_record_start "$@" ;;
        stop|s) macro_record_stop ;;
        play|p) shift; macro_play "$@" ;;
        list|ls|l) macro_list ;;
        delete|rm) shift; rm -f "$MACRO_DIR/${1}.macro" && echo "Deleted: $1" ;;
        *) echo "Usage: macro <record|stop|play|list|delete> [name]" ;;
    esac
}

# FEATURE 16: COMMAND HEATMAP
heatmap() {
[[ -o interactive ]] || { echo "heatmap: needs interactive shell history"; return 1; }
    command -v sort >/dev/null 2>&1 || { echo "heatmap: missing sort"; return 1; }
    command -v awk  >/dev/null 2>&1 || { echo "heatmap: missing awk"; return 1; }
    local days=${1:-30}
    printf "\n%bð¥ COMMAND HEATMAP (last %d days)%b\n\n" "${CYBER_COLORS[magenta]}" "$days" "${CYBER_STYLE[reset]}"
    local -A counts
    local max=0 total=0
    (( total == 0 )) && { echo "heatmap: no history data"; return 0; }
    while IFS= read -r line; do
        local cmd="${line%% *}"
        cmd="${cmd##*;}"
        [[ -z "$cmd" ]] && continue
        counts[$cmd]=$((${counts[$cmd]:-0} + 1))
        ((total++))
        [[ ${counts[$cmd]} -gt $max ]] && max=${counts[$cmd]}
    done < <(fc -l -$((days * 50)) 2>/dev/null)
    local sorted=($(for c in "${(@k)counts}"; do printf '%d %s\n' "${counts[$c]}" "$c"; done | sort -rn | head -15 | awk '{print $2}'))
    for cmd in "${sorted[@]}"; do
        local cnt=${counts[$cmd]} pct=$((cnt * 100 / total)) bar_len=$((cnt * 40 / max))
        local bar="" color
        for ((j=0; j<bar_len; j++)); do bar+="â"; done
        [[ $bar_len -gt 32 ]] && color="${CYBER_COLORS[red]}" || { [[ $bar_len -gt 20 ]] && color="${CYBER_COLORS[yellow]}" || color="${CYBER_COLORS[green]}"; }
        printf "%-12s %b%s%b %4d (%2d%%)\n" "$cmd" "$color" "$bar" "${CYBER_STYLE[reset]}" "$cnt" "$pct"
    done
    printf "\n%bTotal: %d commands%b\n" "${CYBER_COLORS[cyan]}" "$total" "${CYBER_STYLE[reset]}"
}

# FEATURE 17: OUTPUT FOLDING
typeset -gA FOLD_STATES
fold_output() {
    local -a lines=()
    while IFS= read -r line; do lines+=("$line"); done
    [[ ${#lines[@]} -lt 30 ]] && { printf '%s\n' "${lines[@]}"; return; }
    local in_stacktrace=0 fold_start=0 fold_count=0
    for ((i=1; i<=${#lines[@]}; i++)); do
        local line="${lines[$i]}"
        if [[ "$line" =~ "^[[:space:]]*(at |File |Traceback|Error:|Exception:)" ]]; then
            [[ $in_stacktrace -eq 0 ]] && { fold_start=$i; in_stacktrace=1; fold_count=0; }
            ((fold_count++))
        elif [[ $in_stacktrace -eq 1 ]]; then
            if [[ $fold_count -gt 5 ]]; then
                printf "%b━━━ 📚 Stacktrace (%d lines, click to expand) ━━━%b\n" "${CYBER_COLORS[red]}" "$fold_count" "${CYBER_STYLE[reset]}"
            else
                for ((j=fold_start; j<i; j++)); do printf '%s\n' "${lines[$j]}"; done
            fi
            in_stacktrace=0
            printf '%s\n' "$line"
        else
            printf '%s\n' "$line"
        fi
    done
}
foldrun() {
    [[ $# -eq 0 ]] && { echo "Usage: foldrun <command...>"; return 1; }

    case "$1" in
        vim|nvim|less|more|man|ssh|top|htop|nano|ranger)
            eval "$@"
            return $?
        ;;
    esac

    eval "$@" 2>&1 | fold_output
}
alias fr='foldrun'

# FEATURE 18: INTERACTIVE TIMELINE
typeset -ga CYBER_TIMELINE=()
typeset -g CYBER_TIMELINE_MAX=200
timeline_add() {
    local ts=$(date +%s) exit=$1 dur=$2 cmd="$3"
    CYBER_TIMELINE+=("$ts:$exit:$dur:$cmd")
    [[ ${#CYBER_TIMELINE[@]} -gt $CYBER_TIMELINE_MAX ]] && CYBER_TIMELINE=("${CYBER_TIMELINE[@]:1}")
}
timeline() {
(( ${#CYBER_TIMELINE[@]} == 0 )) && { echo "timeline: empty"; return 0; }
    local count=${1:-20}
    printf "\n%b⏱️ COMMAND TIMELINE%b\n\n" "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    local i=${#CYBER_TIMELINE[@]}
    local shown=0
    while [[ $i -gt 0 ]] && [[ $shown -lt $count ]]; do
        local entry="${CYBER_TIMELINE[$i]}"
        IFS=: read -r ts exit dur cmd <<< "$entry"
        local time_str=$(date -d "@$ts" '+%H:%M:%S' 2>/dev/null || date -r "$ts" '+%H:%M:%S' 2>/dev/null || echo "$ts")
        local icon=$([[ $exit -eq 0 ]] && echo "✓" || echo "✗")
        local color=$([[ $exit -eq 0 ]] && echo "${CYBER_COLORS[green]}" || echo "${CYBER_COLORS[red]}")
        printf "%b%s%b [%s] %s %b(%ds)%b\n" "$color" "$icon" "${CYBER_STYLE[reset]}" "$time_str" "${cmd:0:50}" "${CYBER_COLORS[gray]}" "$dur" "${CYBER_STYLE[reset]}"
        ((i--)); ((shown++))
    done
}
timeline_replay() {
    local idx=$1
    [[ $idx -gt 0 ]] && [[ $idx -le ${#CYBER_TIMELINE[@]} ]] && {
        local entry="${CYBER_TIMELINE[-$idx]}"
        local cmd="${entry##*:}"
        printf "%b▶️ Replaying: %s%b\n" "${CYBER_COLORS[cyan]}" "$cmd" "${CYBER_STYLE[reset]}"
        eval "$cmd"
    }
}

# FEATURE 19: GIT UI INLINE
gst() {
    git rev-parse --is-inside-work-tree &>/dev/null || { echo "Not a git repo"; return 1; }
    local branch=$(git branch --show-current 2>/dev/null)
    printf "\n%bâ GIT: %s%b" "${CYBER_COLORS[magenta]}" "$branch" "${CYBER_STYLE[reset]}"
    local ahead=$(git rev-list --count @{upstream}..HEAD 2>/dev/null || echo 0)
    local behind=$(git rev-list --count HEAD..@{upstream} 2>/dev/null || echo 0)
    [[ $ahead -gt 0 ]] && printf " %bâ%d%b" "${CYBER_COLORS[green]}" "$ahead" "${CYBER_STYLE[reset]}"
    [[ $behind -gt 0 ]] && printf " %bâ%d%b" "${CYBER_COLORS[red]}" "$behind" "${CYBER_STYLE[reset]}"
    printf "\n\n"
    local staged=$(git diff --cached --name-only 2>/dev/null | wc -l)
    local unstaged=$(git diff --name-only 2>/dev/null | wc -l)
    local untracked=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l)
    [[ $staged -gt 0 ]] && { printf "%bð¦ Staged (%d):%b\n" "${CYBER_COLORS[green]}" "$staged" "${CYBER_STYLE[reset]}"; git diff --cached --name-only | head -5 | sed 's/^/  + /'; }
    [[ $unstaged -gt 0 ]] && { printf "%bð Modified (%d):%b\n" "${CYBER_COLORS[yellow]}" "$unstaged" "${CYBER_STYLE[reset]}"; git diff --name-only | head -5 | sed 's/^/  ~ /'; }
    [[ $untracked -gt 0 ]] && { printf "%bâ Untracked (%d):%b\n" "${CYBER_COLORS[red]}" "$untracked" "${CYBER_STYLE[reset]}"; git ls-files --others --exclude-standard | head -5 | sed 's/^/  ? /'; }
    printf "\n%b[a]%b Add all  %b[c]%b Commit  %b[p]%b Push  %b[d]%b Diff\n" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}"
    read -sk1 -t 3 key 2>/dev/null
    case "$key" in
        a) git add -A && printf "%bâ Staged all%b\n" "${CYBER_COLORS[green]}" "${CYBER_STYLE[reset]}" ;;
        c) git commit -v ;;
        p) git push ;;
        d) git diff | bat --language=diff --style=plain 2>/dev/null || git diff ;;
    esac
}
gdf() { git diff "$@" | bat --language=diff --style=plain 2>/dev/null || git diff "$@"; }

# FEATURE 20: VISUAL CONFIRMATIONS
typeset -g CYBER_NOTIFY_LAST=""
typeset -g CYBER_NOTIFY_LAST_T=0
typeset -g CYBER_NOTIFY_COOLDOWN=2

cyber_notify_box() {
    local color="$1" label="$2" msg="$3"
    local cols=${COLUMNS:-80}
    local inner=$(( cols - 6 ))
    (( inner < 30 )) && inner=30

    local text="⟦${label}⟧ ${msg}"
    if (( ${#text} > inner )); then
        text="${text[1,$inner]}"
    fi
    local pad=$(( inner - ${#text} ))
    (( pad < 0 )) && pad=0
    local spaces=""
    (( pad > 0 )) && spaces="$(printf "%*s" "$pad" "")"

    printf "\n%b╭─%b %s%s %b─╮%b\n" "${CYBER_COLORS[$color]}" "${CYBER_STYLE[reset]}" "$text" "$spaces" "${CYBER_COLORS[$color]}" "${CYBER_STYLE[reset]}"
    printf "%b╰%b%*s%b╯%b\n" "${CYBER_COLORS[$color]}" "${CYBER_STYLE[reset]}" "$((inner+2))" "" "${CYBER_COLORS[$color]}" "${CYBER_STYLE[reset]}"
}

cyber_notify_once() {
    local key="$1"; shift
    local now=$EPOCHSECONDS
    if [[ "$key" == "$CYBER_NOTIFY_LAST" && $((now - CYBER_NOTIFY_LAST_T)) -lt $CYBER_NOTIFY_COOLDOWN ]]; then
        return
    fi
    CYBER_NOTIFY_LAST="$key"
    CYBER_NOTIFY_LAST_T=$now
    "$@"
}

show_success() { cyber_notify_once "ok:$1" cyber_notify_box green "✓" "${1:-Done}"; }
show_warning() { cyber_notify_once "warn:$1" cyber_notify_box yellow "⚠" "${1:-Warning}"; }
show_error()   { cyber_notify_once "err:$1" cyber_notify_box red "✖" "${1:-Error}"; }

# FEATURE 21: SMART SUDO
typeset -ga SUDO_REQUIRED=("pacman -S" "pacman -R" "pacman -U" "systemctl start" "systemctl stop" "systemctl restart" "systemctl enable" "systemctl disable" "mount" "umount" "fdisk" "mkfs" "chown" "chmod 000" "useradd" "userdel")
needs_sudo() { local cmd="$1"; for p in "${SUDO_REQUIRED[@]}"; do [[ "$cmd" == "$p"* ]] && return 0; done; return 1; }
smart_sudo() {
    local cmd="$*"
    [[ "$cmd" == sudo* ]] && { eval "$cmd"; return; }
    needs_sudo "$cmd" && {
        printf "%bð Needs sudo: %s%b\n" "${CYBER_COLORS[yellow]}" "$cmd" "${CYBER_STYLE[reset]}"
        sudo $cmd
    } || eval "$cmd"
}
cyber_accept_line() {
    local cmd="$BUFFER"
    [[ -z "$cmd" ]] && { zle accept-line; return; }

    if needs_sudo "$cmd" && [[ "$cmd" != sudo\ * ]]; then
        BUFFER="sudo $cmd"
        zle -M "Needs sudo → added automatically"
    fi

    zle accept-line
}
zle -N cyber_accept_line
# bindkey '^M' cyber_accept_line   # DEZACTIVAT - interferează cu navigarea
# bindkey '^J' cyber_accept_line   # DEZACTIVAT

# FEATURE 22: AMBIENT MODE
typeset -g AMBIENT_TIMEOUT=300
typeset -g AMBIENT_ACTIVE=0
typeset -g CYBER_LAST_ACTIVITY=$(date +%s)
enter_ambient_mode() {
    AMBIENT_ACTIVE=1
    [[ "$TERM" == *"kitty"* ]] && { printf '\033]10;#505060\007'; printf '\033]11;#080810\007'; }
    printf '\033[?12l\033[2 q'
}
exit_ambient_mode() {
    AMBIENT_ACTIVE=0
    [[ "$TERM" == *"kitty"* ]] && { printf '\033]10;#e0e0e0\007'; printf '\033]11;#0a0a12\007'; }
    printf '\033[?12h\033[6 q'
}
update_activity() { CYBER_LAST_ACTIVITY=$(date +%s); [[ $AMBIENT_ACTIVE -eq 1 ]] && exit_ambient_mode; }
cyber_ambient_tick() {
    [[ -t 1 ]] || return
    local now=$(date +%s)
    if (( AMBIENT_ACTIVE == 0 )) && (( now - CYBER_LAST_ACTIVITY > AMBIENT_TIMEOUT )); then
        enter_ambient_mode
        typeset -f cyber_draw_utility_bar >/dev/null 2>&1 && cyber_draw_utility_bar
    fi
}

TRAPUSR1() { cyber_ambient_tick; return 0; }

cyber_start_ambient_watchdog() {
    [[ -o interactive ]] || return
    typeset -g CYBER_AMBIENT_WATCHDOG_PID=${CYBER_AMBIENT_WATCHDOG_PID:-0}
    if (( CYBER_AMBIENT_WATCHDOG_PID > 0 )) && kill -0 $CYBER_AMBIENT_WATCHDOG_PID 2>/dev/null; then
        return
    fi
    (
        while true; do
            sleep 3
            kill -USR1 $$ 2>/dev/null || exit 0
        done
    ) &
    CYBER_AMBIENT_WATCHDOG_PID=$!
    disown $CYBER_AMBIENT_WATCHDOG_PID 2>/dev/null
}

cyber_start_ambient_watchdog

# FEATURE 23: TERMINAL AGENT (@)
agent() {
    local request="$*"
    local req_lower="${request:l}"
    if [[ "$req_lower" =~ "instal" ]]; then
        local pkg=$(echo "$request" | grep -oP '(?:install|instaleazÄ)\s+\K\S+')
        [[ -n "$pkg" ]] && {
            printf "%bð Searching: %s%b\n" "${CYBER_COLORS[cyan]}" "$pkg" "${CYBER_STYLE[reset]}"
            local found=($(yay -Ssq "$pkg" 2>/dev/null | head -5))
            [[ ${#found[@]} -eq 0 ]] && { echo "Not found: $pkg"; return; }
            if [[ ${#found[@]} -eq 1 ]]; then
                printf "%bInstall %s? [y/n]%b " "${CYBER_COLORS[yellow]}" "${found[1]}" "${CYBER_STYLE[reset]}"
                read -k1 ans; echo
                [[ "$ans" == "y" ]] && yay -S "${found[1]}"
            else
                printf "%bFound:%b\n" "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
                local i=1; for p in "${found[@]}"; do printf "  [%d] %s\n" "$i" "$p"; ((i++)); done
                printf "Choice: "; read choice
                [[ $choice -gt 0 ]] && [[ $choice -le ${#found[@]} ]] && yay -S "${found[$choice]}"
            fi
        }
    elif parse_intent "$request" 2>/dev/null; then
        return
    else
        printf "%bð¤ Not sure about: %s%b\n" "${CYBER_COLORS[yellow]}" "$request" "${CYBER_STYLE[reset]}"
        printf "Try: 'instaleazÄ X', 'vreau server', 'curÄÈÄ cache'\n"
    fi
}
alias '@'='agent'

# FEATURE 24: CONTEXT AWARENESS
typeset -g CURRENT_PROJECT="" CURRENT_PROJECT_TYPE=""
detect_project() {
    CURRENT_PROJECT="" CURRENT_PROJECT_TYPE=""
    [[ -f "package.json" ]] && { CURRENT_PROJECT_TYPE="nodejs"; CURRENT_PROJECT=$(jq -r '.name // "nodejs"' package.json 2>/dev/null); }
    [[ -f "Cargo.toml" ]] && { CURRENT_PROJECT_TYPE="rust"; CURRENT_PROJECT=$(grep -m1 'name' Cargo.toml 2>/dev/null | cut -d'"' -f2); }
    [[ -f "setup.py" ]] || [[ -f "pyproject.toml" ]] && { CURRENT_PROJECT_TYPE="python"; CURRENT_PROJECT=$(basename "$PWD"); }
    [[ -f "CMakeLists.txt" ]] || [[ -f "Makefile" ]] && { CURRENT_PROJECT_TYPE="cpp"; CURRENT_PROJECT=$(basename "$PWD"); }
    [[ -d ".git" ]] && [[ -z "$CURRENT_PROJECT_TYPE" ]] && { CURRENT_PROJECT_TYPE="git"; CURRENT_PROJECT=$(basename "$PWD"); }
}
project_suggestions() {
    case "$CURRENT_PROJECT_TYPE" in
        nodejs) echo "npm run dev | npm test | npm build" ;;
        rust) echo "cargo run | cargo test | cargo build --release" ;;
        python) echo "python main.py | pytest | pip install -r requirements.txt" ;;
        cpp) echo "make | cmake .. | make clean" ;;
        git) echo "git status | git pull | git push" ;;
    esac
}


# UTILITY BAR (persistent status)
render_status_bar() { typeset -f cyber_draw_utility_bar >/dev/null 2>&1 && cyber_draw_utility_bar; }

# UTILITY FUNCTIONS
ex() {
    [[ ! -f "$1" ]] && { echo "Not a file: $1"; return 1; }
    case "$1" in
        *.tar.bz2|*.tbz2) tar xjf "$1" ;; *.tar.gz|*.tgz) tar xzf "$1" ;; *.tar.xz) tar xJf "$1" ;;
        *.bz2) bunzip2 "$1" ;; *.gz) gunzip "$1" ;; *.tar) tar xf "$1" ;;
        *.zip) unzip "$1" ;; *.7z) 7z x "$1" ;; *.rar) unrar x "$1" ;;
        *.xz) unxz "$1" ;; *.zst) unzstd "$1" ;;
        *) echo "Cannot extract: $1" ;;
    esac
}
mkcd() { mkdir -p "$1" && cd "$1"; }
backup() { cp -r "$1" "${1}.backup_$(date +%Y%m%d_%H%M%S)"; echo "Backed up: $1"; }
trash() { local d="$HOME/.local/share/Trash/files"; mkdir -p "$d"; mv "$@" "$d/"; echo "Trashed: $*"; }
largest() { du -ah . 2>/dev/null | sort -rh | head -${1:-10}; }
killport() { local p=$(lsof -ti:"$1" 2>/dev/null); [[ -n "$p" ]] && kill -9 "$p" && echo "Killed on port $1" || echo "Nothing on port $1"; }
sysinfo() {
    printf "\n%bð¥ï¸ SYSTEM INFO%b\n" "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    printf "OS: %s\nKernel: %s\nHost: %s\nUser: %s\nShell: %s\nUptime: %s\nMemory: %s\nDisk: %s\n" \
        "$(uname -o)" "$(uname -r)" "$(hostname)" "$USER" "$SHELL" \
        "$(uptime -p 2>/dev/null || echo 'N/A')" \
        "$(free -h | awk '/Mem:/{print $3"/"$2}')" \
        "$(df -h / | awk 'NR==2{print $3"/"$2}')"
}
update() { printf "%bð Updating...%b\n" "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"; yay -Syu --noconfirm 2>/dev/null || sudo pacman -Syu --noconfirm; printf "%bâ Done%b\n" "${CYBER_COLORS[green]}" "${CYBER_STYLE[reset]}"; }
cleanup() {
    printf "%bð§¹ Cleaning...%b\n" "${CYBER_COLORS[cyan]}" "${CYBER_STYLE[reset]}"
    sudo pacman -Sc --noconfirm 2>/dev/null
    local orphans=$(pacman -Qtdq 2>/dev/null); [[ -n "$orphans" ]] && sudo pacman -Rns $orphans --noconfirm
    rm -rf ~/.cache/* 2>/dev/null
    sudo journalctl --vacuum-time=7d 2>/dev/null
    printf "%bâ Cleaned%b\n" "${CYBER_COLORS[green]}" "${CYBER_STYLE[reset]}"
}

# ERROR HANDLER
ERROR_MSGS=("'%s' nu existÄ. Nice try." "'%s' a fost cÄutat. Nu a fost gÄsit." "Comanda '%s' a eÈuat Ã®nainte sÄ Ã®nceapÄ." "'%s' nu e o comandÄ. E doar text." "Nimic nu rÄspunde la '%s'." "'%s' pare o comandÄ. Nu este." "Shell-ul refuzÄ sÄ execute '%s'.")
command_not_found_handler() {
    local cmd="$1"
    local msg="${ERROR_MSGS[$((RANDOM % ${#ERROR_MSGS[@]} + 1))]}"
    printf "\n %b╭────────── ⚠️  ────────── COMMAND NOT FOUND ─────────────────────────────────────────╮%b\n" "${CYBER_COLORS[red]}" "${CYBER_STYLE[reset]}"
    printf "  %b│%b  $msg\n" "${CYBER_COLORS[red]}" "${CYBER_STYLE[reset]}" "$cmd"
    printf "  %b╰───────────────────────────────────────────────────────────────────╯%b\n" "${CYBER_COLORS[red]}" "${CYBER_STYLE[reset]}"
    local similar=$(find_closest_command "$cmd" 2>/dev/null)
    [[ -n "$similar" ]] && printf "  %b💡 Maybe: %s%b\n" "${CYBER_COLORS[green]}" "$similar" "${CYBER_STYLE[reset]}"
    command -v pacman &>/dev/null && {
        local pkg=$(pacman -F "$cmd" 2>/dev/null | grep -m1 "is owned by" | awk '{print $NF}')
        [[ -n "$pkg" ]] && printf "  %bð¦ Install: sudo pacman -S %s%b\n" "${CYBER_COLORS[cyan]}" "$pkg" "${CYBER_STYLE[reset]}"
    }
    return 127
}

# HOOKS
preexec() {
    typeset -f cyber_preexec_capture_stderr >/dev/null 2>&1 && cyber_preexec_capture_stderr
    typeset -f cyber_disable_mouse >/dev/null 2>&1 && cyber_disable_mouse
    (( CYBER_TOPBAR_ENABLED )) && cyber_clear_utility_bar 2>/dev/null
    CYBER_LAST_COMMAND="$1"
    CYBER_LAST_COMMAND_TIME=$EPOCHSECONDS
    CYBER_TERMINAL_BUSY=1
    update_activity
    [[ $CYBER_RECORDING_MACRO -eq 1 ]] && macro_add_command "$1"
}
precmd() {
    local last_exit=$?
    # typeset -f cyber_precmd_restore_stderr_doctor_and_bar >/dev/null 2>&1 && cyber_precmd_restore_stderr_doctor_and_bar "$last_exit"
    typeset -f cyber_enable_mouse >/dev/null 2>&1 && cyber_enable_mouse
    CYBER_LAST_EXIT_CODE=$last_exit
    local dur=0
    [[ -n "$CYBER_LAST_COMMAND_TIME" ]] && dur=$((EPOCHSECONDS - CYBER_LAST_COMMAND_TIME))
    CYBER_TERMINAL_BUSY=0

    [[ -n "$CYBER_LAST_COMMAND" ]] && {
        update_command_frequency "$CYBER_LAST_COMMAND"
        record_command_sequence "$CYBER_LAST_COMMAND"
        timeline_add $CYBER_LAST_EXIT_CODE $dur "$CYBER_LAST_COMMAND"
        [[ $dur -gt 10 ]] && printf "%b⏱ %ds%b\n" "${CYBER_COLORS[cyan]}" "$dur" "${CYBER_STYLE[reset]}"
        [[ $CYBER_LAST_EXIT_CODE -ne 0 ]] && [[ $CYBER_LAST_EXIT_CODE -ne 127 ]] && predict_next_command
    }

    detect_project
    CYBER_LAST_COMMAND="" CYBER_LAST_COMMAND_TIME=0
}
# Forțează redesenarea barei după fiecare comandă
_cyber_redraw_bar_precmd() {
    (( CYBER_TOPBAR_ENABLED )) && cyber_draw_utility_bar 2>/dev/null
}
add-zsh-hook precmd _cyber_redraw_bar_precmd

# KEY BINDINGS
bindkey -e
bindkey '^[[C' forward-char        # Săgeată dreapta
bindkey '^[[D' backward-char       # Săgeată stânga
bindkey '^A' beginning-of-line
bindkey '^E' end-of-line
bindkey '^B' backward-char
bindkey '^F' forward-char
bindkey '^P' up-line-or-history
bindkey '^N' down-line-or-history
bindkey '^[[A' history-substring-search-up 2>/dev/null
bindkey '^[[B' history-substring-search-down 2>/dev/null
bindkey '^[[H' beginning-of-line
bindkey '^[[F' end-of-line
bindkey '^[[3~' delete-char
bindkey '^[[1;5C' forward-word
bindkey '^[[1;5D' backward-word
bindkey '^H' backward-kill-word
bindkey '^R' history-incremental-search-backward
bindkey '^ ' file_explorer_widget
bindkey '^X^C' toggle_clipboard_bar


# FZF
[[ -f /usr/share/fzf/key-bindings.zsh ]] && source /usr/share/fzf/key-bindings.zsh
[[ -f /usr/share/fzf/completion.zsh ]] && source /usr/share/fzf/completion.zsh


# DEV ENVIRONMENT
export NVM_DIR="$HOME/.nvm"
[[ -s "$NVM_DIR/nvm.sh" ]] && \. "$NVM_DIR/nvm.sh"
[[ -f "$HOME/.cargo/env" ]] && . "$HOME/.cargo/env"
export GOPATH="$HOME/go"
export PATH="$HOME/.local/bin:$GOPATH/bin:$PATH"
command -v direnv &>/dev/null && eval "$(direnv hook zsh)"

# P10K
# [[ -r ~/.p10k.zsh ]] && source ~/.p10k.zsh
# [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]] && source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"

# FINAL PLUGINS
if [[ -o interactive ]]; then
    zinit ice lucid wait"19" atload"_zsh_autosuggest_start"
    zinit light zsh-users/zsh-autosuggestions
    zinit ice lucid wait"20"
    zinit light zsh-users/zsh-syntax-highlighting
fi

# INIT
mkdir -p "$CYBER_DATA_DIR"/{history,macros,profiles,clipboard,timelines} "$CYBER_CACHE_DIR" "$CYBER_CONFIG_DIR" 2>/dev/null
load_command_frequency
load_command_sequences
clipboard_load
detect_project
if [[ -o interactive ]] && [[ -z "$WELCOME_SHOWN" ]]; then
  WELCOME_SHOWN=1
  CYBER_TOPBAR_ENABLED=0
  cinematic_intro
  CYBER_TOPBAR_ENABLED=1
fi
if [[ -o interactive ]] && (( PARALLAX_ENABLED )); then
  parallax_start
fi

# HELP
help_commands() {
    printf "\n%b📚 CYBER SHELL COMMANDS%b\n\n" "${CYBER_COLORS[magenta]}" "${CYBER_STYLE[reset]}"
    printf "%b🤖 AGENT%b\n" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}"
    printf "  @ <request>     Natural language commands\n"
    printf "  ? <query>       Search docs/man/cheat.sh\n\n"
    printf "%b📼 MACROS%b\n" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}"
    printf "  macro record <n>  Start recording\n"
    printf "  macro stop        Stop recording\n"
    printf "  macro play <n>    Play macro\n"
    printf "  macro list        List macros\n\n"
    printf "%b📊 ANALYTICS%b\n" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}"
    printf "  heatmap           Command usage heatmap\n"
    printf "  timeline          Command timeline\n\n"
    printf "%b⎇ GIT%b\n" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}"
    printf "  gst               Visual git status\n"
    printf "  gdf               Inline diff\n\n"
    printf "%b🔧 SYSTEM%b\n" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}"
    printf "  sysinfo           System info\n"
    printf "  update            Update system\n"
    printf "  cleanup           Clean cache & orphans\n\n"
    printf "%b⌨️ SHORTCUTS%b\n" "${CYBER_COLORS[yellow]}" "${CYBER_STYLE[reset]}"
    printf "  Ctrl+Space        File explorer\n"
    printf "  Ctrl+X Ctrl+C     Clipboard bar\n\n"
}
# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
# SECTION 14: FEATURE 3 - INTELLIGENT CURSOR
# \u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550

# Cursor states
typeset -gA CURSOR_STATES
CURSOR_STATES=(
    [normal]='\033[6 q'
    [insert]='\033[5 q'
    [sudo]='\033[1 q'
    [danger]='\033[2 q'
    [busy]='\033[3 q'
)

# Cursor colors (for terminals that support it)
typeset -gA CURSOR_COLORS
CURSOR_COLORS=(
    [normal]='\033]12;#00ffff\007'
    [sudo]='\033]12;#ff00ff\007'
    [danger]='\033]12;#ff0055\007'
    [busy]='\033]12;#ffff00\007'
)
# Detect dangerous commands (fast, glob-based)
is_dangerous_command() {
    local cmd="$1"

    # trim spaces
    cmd="${cmd#"${cmd%%[![:space:]]*}"}"
    cmd="${cmd%"${cmd##*[![:space:]]}"}"
    [[ -z "$cmd" ]] && return 1

    # strip leading sudo
    if [[ "$cmd" == sudo\ * ]]; then
        cmd="${cmd#sudo }"
        cmd="${cmd#"${cmd%%[![:space:]]*}"}"
    fi

    local head="${cmd%% *}"

    case "$head" in
        rm)
            # rm -rf / , rm -rf /* , rm -rf ~ (or home), no-preserve-root
            [[ "$cmd" == rm\ -rf\ / ]] && return 0
            [[ "$cmd" == rm\ -rf\ /* ]] && return 0
            [[ "$cmd" == rm\ -rf\ ~ ]] && return 0
            [[ "$cmd" == rm\ -rf\ ~/* ]] && return 0
            [[ "$cmd" == --no-preserve-root ]] && return 0
            ;;
        dd)
            # writing to block devices
            [[ "$cmd" == dd\ of=/dev/ ]] && return 0
            ;;
        mkfs*|wipefs|shred|fdisk|parted)
            [[ "$cmd" == \ /dev/ ]] && return 0
            ;;
        chmod)
            [[ "$cmd" == chmod\ 000\ * ]] && return 0
            [[ "$cmd" == chmod\ -R\ 000\ * ]] && return 0
            ;;
        chown)
            [[ "$cmd" == chown\ -R\ \ / ]] && return 0
            ;;
    esac

    # obvious destructive redirections
    [[ "$cmd" == '>/dev/' ]] && return 0

    # fork bomb-ish
    [[ "$cmd" == ':(){'':|:'* ]] && return 0

    return 1
}
# Current cursor state
typeset -g CURRENT_CURSOR_STATE="normal"

# Update cursor based on command line content
update_cursor_state() {
    local buffer="$BUFFER"
    local new_state="normal"

    # Check if sudo
    if [[ "$buffer" == sudo* ]] || [[ "$buffer" == *"sudo "* ]]; then
        new_state="sudo"
        CYBER_IS_SUDO=1
    else
        CYBER_IS_SUDO=0
    fi

    # Check if dangerous
    if is_dangerous_command "$buffer"; then
        new_state="danger"
        CYBER_IS_DANGEROUS=1
    else
        CYBER_IS_DANGEROUS=0
    fi

    # Check if terminal is busy
    if [[ $CYBER_TERMINAL_BUSY -eq 1 ]]; then
        new_state="busy"
    fi

    # Update cursor if state changed
    if [[ "$new_state" != "$CURRENT_CURSOR_STATE" ]]; then
        CURRENT_CURSOR_STATE="$new_state"
        apply_cursor_state
    fi
}

# Apply cursor state
apply_cursor_state() {
    local state="${CURRENT_CURSOR_STATE:-normal}"

    # Set cursor shape
    printf '%b' "${CURSOR_STATES[$state]}"

    # Set cursor color (Kitty/compatible terminals)
    if [[ "$TERM" == *"kitty"* ]]; then
        printf '%b' "${CURSOR_COLORS[$state]}"
    fi
}

# Cursor pulse animation for busy state
cursor_pulse() {
    local duration=${1:-0.5}
    local end_time=$((EPOCHREALTIME + duration))

    while (( EPOCHREALTIME < end_time )); do
        printf '\033[?12h'  # Blinking on
        sleep 0.1
        printf '\033[?12l'  # Blinking off
        sleep 0.1
    done
}

# ZLE widget for cursor update
cursor_update_widget() {
    update_cursor_state
    zle -M ""
}

# Register the widget
zle -N cursor_update_widget
zle-line-init() {
    cursor_update_widget 2>/dev/null
}
zle -N zle-line-init
zle-keymap-select() {
    cursor_update_widget 2>/dev/null
}
zle -N zle-keymap-select
zle-line-finish() { cursor_update_widget; }
zle -N zle-line-finish
