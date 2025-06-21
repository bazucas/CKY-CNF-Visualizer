import tkinter as tk
from tkinter import font as tkfont, messagebox
import re
from collections import defaultdict

# ─────────────  Traduções  ─────────────
TR = {
    'pt': {'grammar':'Gramática (CNF):','sentence':'Frase:',
           'calc':'Calcular','table':'Tabela CKY',
           'accepted':'✔️  A frase é gerada.',
           'rejected':'❌  NÃO é gerada.',
           'error':'Gramática vazia ou mal formatada.'},

    'en': {'grammar':'Grammar (CNF):','sentence':'Sentence:',
           'calc':'Calculate','table':'CKY Table',
           'accepted':'✔️  Sentence accepted.',
           'rejected':'❌  Sentence rejected.',
           'error':'Grammar empty or bad.'},

    'fr': {'grammar':'Grammaire (FNC):','sentence':'Phrase :',
           'calc':'Calculer','table':'Table CKY',
           'accepted':'✔️  Phrase générée.',
           'rejected':'❌  Phrase rejetée.',
           'error':'Grammaire vide ou mal formée.'}
}
FLAGS={'pt':'PT','en':'EN','fr':'FR'}

# ─────────────  Parser CNF  ─────────────
def parse_cnf(lines):
    lhs=set(); NT=re.compile(r'^[A-Z][_A-Za-z0-9]*$')
    for ln in lines:
        if '->' not in ln: raise ValueError
        left=ln.split('->',1)[0].strip()
        if not NT.match(left): raise ValueError
        lhs.add(left)

    unary,binary=defaultdict(set),defaultdict(set)
    for ln in lines:
        left,rhs=map(str.strip,ln.split('->',1))
        for alt in rhs.split('|'):
            syms=alt.strip().split()
            if len(syms)==1:
                tok=re.sub(r"""^(['"])(.*)\1$""",r'\2',syms[0])
                if tok not in lhs: unary[tok].add(left); continue
            if len(syms)==2 and all(s in lhs for s in syms):
                binary[tuple(syms)].add(left)
            else: raise ValueError
    return unary,binary

# ─────────────  CKY + back-pointers  ─────────────
def cky_bp(tokens, unary, binary):
    n=len(tokens)
    table=[[set() for _ in range(n)] for _ in range(n)]
    back=[[defaultdict(list) for _ in range(n)] for _ in range(n)]

    for j,tok in enumerate(tokens):
        for A in unary.get(tok,[]):
            table[0][j].add(A)
            back[0][j][A]=[(tok,)]            # folha

    for length in range(2,n+1):
        for start in range(n-length+1):
            for split in range(1,length):
                L=table[split-1][start]
                R=table[length-split-1][start+split]
                for B in L:
                    for C in R:
                        for A in binary.get((B,C),[]):
                            table[length-1][start].add(A)
                            back[length-1][start][A].append((split,B,C))
    return table,back

# ─────────────  GUI  ─────────────
class CKYGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CKY Visualizer")
        self.geometry("1500x750")             # ↓ ligeiramente mais baixo
        self.lang='pt'
        self.font_m=tkfont.Font(family='Consolas',size=12)
        self.last=None
        self._ui(); self._translate()

    # ---------- UI ----------
    def _ui(self):
        top=tk.Frame(self); top.pack(fill='x',padx=8,pady=4)
        self.btn=tk.Button(top,command=self._calc); self.btn.pack(side='left')
        self.lang_var=tk.StringVar(value=FLAGS[self.lang])
        tk.OptionMenu(top,self.lang_var,*FLAGS.values(),command=self._chg).pack(side='right')

        self.lbl_g=tk.Label(self,anchor='w'); self.lbl_g.pack(fill='x',padx=8)
        self.txt_g=tk.Text(self,height=6,font=self.font_m); self.txt_g.pack(fill='x',padx=8)
        self.txt_g.insert('1.0',
            "S -> NP VP\nNP -> Det N\nVP -> V NP\n"
            "Det -> As | muita\nN -> verdades | gente\nV -> incomodam")
        sf=tk.Frame(self); sf.pack(fill='x',padx=8)
        self.lbl_s=tk.Label(sf); self.lbl_s.pack(side='left')
        self.ent_s=tk.Entry(sf,font=self.font_m); self.ent_s.pack(fill='x',expand=True,padx=(4,0))
        self.ent_s.insert(0,"As verdades incomodam muita gente")

        main=tk.Frame(self); main.pack(fill='both',expand=True,padx=8,pady=6)
        # pirâmide encostada ao topo (anchor='n')
        self.tbl=tk.Frame(main,relief='groove',borderwidth=1)
        self.tbl.pack(side='left',anchor='n')
        self.canvas=tk.Canvas(main,bg='white')
        self.canvas.pack(side='left',fill='both',expand=True,padx=(8,0))

    def _translate(self):
        t=TR[self.lang]
        self.btn.config(text=t['calc'])
        self.lbl_g.config(text=t['grammar'])
        self.lbl_s.config(text=t['sentence'])
        if self.last: self._redraw(*self.last)

    def _chg(self,*_):
        self.lang={v:k for k,v in FLAGS.items()}[self.lang_var.get()]
        self._translate()

    # ---------- cálculo ----------
    def _calc(self):
        lines=[ln.strip() for ln in self.txt_g.get('1.0','end').splitlines() if ln.strip()]
        toks=self.ent_s.get().split()
        try: u,b=parse_cnf(lines)
        except ValueError:
            messagebox.showerror("CKY",TR[self.lang]['error']); return
        table,back=cky_bp(toks,u,b)
        self.last=(toks,table,back)
        self._redraw(*self.last)

    # ---------- redraw ----------
    def _redraw(self,toks,table,back):
        self._draw_table(toks,table,back)
        self._draw_tree(toks,table,back)

    # ---------- Tabela (triângulo cima-direita) ----------
    def _draw_table(self,toks,table,back):
        for w in self.tbl.winfo_children(): w.destroy()

        n=len(toks); cw,ch=95,42
        canv=tk.Canvas(self.tbl,bg='#f7f7f7',
                       width=(n+1)*cw, height=(n+2)*ch)
        canv.grid(row=0,column=0)

        canv.create_text((n+1)*cw/2,14,
                         text=TR[self.lang]['table'],
                         font=('Helvetica',14,'bold'))

        # palavras — começam logo na 1.ª coluna
        base_y=(n+1)*ch
        for j,tok in enumerate(toks):
            x=j*cw + cw/2
            canv.create_text(x, base_y+14, text=tok, font=self.font_m)

        # células (row=n-length, col=start)
        for length in range(1,n+1):
            row=n-length
            for start in range(n-length+1):
                col=start
                x0,y0=col*cw, row*ch + ch
                x1,y1=x0+cw,y0+ch
                txt=", ".join(sorted(table[length-1][start]))
                canv.create_rectangle(x0,y0,x1,y1,outline='black')
                canv.create_text((x0+x1)/2,(y0+y1)/2,text=txt,font=self.font_m)

        # setas
        def center(l,s):
            # l (length) >=1, s (start) >=0
            row=n-l
            col=s
            return col*cw+cw/2, row*ch + ch + ch/2

        for l in range(2,n+1):
            for s in range(n-l+1):
                for lst in back[l-1][s].values():
                    if not lst or len(lst[0])==1: continue
                    split,_,_=lst[0]
                    cx,cy=center(l,s)
                    lx,ly=center(split,s)
                    rx,ry=center(l-split,s+split)
                    canv.create_line(cx,cy-5,lx,ly+5,arrow=tk.LAST,width=1)
                    canv.create_line(cx,cy-5,rx,ry+5,arrow=tk.LAST,width=1)

    # ---------- Árvore (inalterada) ----------
    def _draw_tree(self,toks,table,back):
        self.canvas.delete('all')
        n=len(toks)
        if 'S' not in table[-1][0]: return

        def build(sym,i,j):
            if any(len(e)==1 for e in back[i][j][sym]):
                tok=next(e[0] for e in back[i][j][sym] if len(e)==1)
                return sym,[(tok,[],(j,j),True)],(j,j)
            for split,B,C in back[i][j][sym]:
                if B in table[split-1][j] and C in table[i-split][j+split]:
                    L=build(B,split-1,j)
                    R=build(C,i-split,j+split)
                    return sym,[L,R],(L[2][0],R[2][1])
            return sym,[],(j,j)

        root=build('S',n-1,0)
        xs,ys=115,75
        def draw(node,lvl):
            lab,kids,span,*rest=node
            is_tok=rest[0] if rest else False
            mid=(span[0]+span[1])*xs/2 + xs
            y=lvl*ys+20
            if not is_tok:
                self.canvas.create_text(mid,y,text=lab,
                                        font=('Helvetica',14,'bold'))
            else:
                self.canvas.create_text(mid,y,text=lab,
                                        font=self.font_m,fill='blue')
            for ch in kids:
                cmid=(ch[2][0]+ch[2][1])*xs/2 + xs
                cy=(lvl+1)*ys+20
                self.canvas.create_line(mid,y+5,cmid,cy-5)
                draw(ch,lvl+1)
        self.canvas.config(scrollregion=(0,0,(n+2)*xs,13*ys))
        draw(root,0)

# ─────────────  MAIN  ─────────────
if __name__=='__main__':
    CKYGui().mainloop()
