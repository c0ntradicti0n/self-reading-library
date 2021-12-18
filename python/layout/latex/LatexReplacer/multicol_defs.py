defs = r"""
\usepackage[colaction]{multicol}
\usepackage{etoolbox}

\makeatletter
\newcounter{nexprex@col@count}
\newcounter{nexprex@current@column@call}
\def\nexprex@patch@last
  {%
    \stepcounter{nexprex@col@count}%
    \protected@write\@auxout{}
      {%
        \string\def\string\nexprex@cur@col{\arabic{nexprex@col@count}}%
      }%
  }
\def\nexprex@patch@else
  {%
    \ifmc@firstcol
      \setcounter{nexprex@col@count}{0}%
    \fi
    \nexprex@patch@last
  }
\def\nexprex@patch@error
  {%
    \GenericError{}
      {Patching of \string\mc@col@status@write\space failed}
      {%
        Make sure `colaction` was set as an option for `multicol`.%
        \MessageBreak
        Else you're screwed, don't use the code provided here.\MessageBreak%
      }
      {No further help available.}%
  }
\pretocmd\mc@lastcol@status@write{\nexprex@patch@last}{}{\nexprex@patch@error}
\pretocmd\mc@col@status@write{\nexprex@patch@else}{}{\nexprex@patch@error}
\newcommand\currentcolumn
  {%
    \stepcounter{nexprex@current@column@call}%
    \protected@write\@auxout{}
      {%
        \string\expandafter
        \string\global
        \string\expandafter
        \string\let
          \string\csname\space
            nexprex@current@column@\arabic{nexprex@current@column@call}%
          \string\endcsname
          \string\nexprex@cur@col
      }%
    \ifcsname
      nexprex@current@column@\arabic{nexprex@current@column@call}\endcsname
      \csname
        nexprex@current@column@\arabic{nexprex@current@column@call}\endcsname
    \fi
  }

\makeatother
"""



multicol_begin = r"""
\begin{multicols}{%s}
"""

multicol_end = r"""
\end{multicols}
"""