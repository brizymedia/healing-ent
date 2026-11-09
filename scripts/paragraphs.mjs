export const READABILITY_STYLE = '<style data-readability="paragraphs-v1">.body p,.faq p,main .sbody p:not(.eyebrow){display:block;margin:0 0 1.15em;line-height:1.95}.lead{display:block}.body .tip>p,.case-story .takeaway>p{margin:0 0 1em;line-height:1.95}.body .tip>p:last-child,.case-story .takeaway>p:last-child{margin-bottom:0}</style>';
const VOID=new Set('area base br col embed hr img input link meta param source track wbr'.split(' '));
export function paragraphChunks(inner){
 const chunks=[],stack=[];let buf='',sentences=0,chars=0;
 const flush=()=>{if(buf.trim())chunks.push(buf.trim());buf='';sentences=0;chars=0;};
 const tokens=String(inner).match(/<[^>]+>|[^<]+/g)||[];
 let breaks=0;
 for(const token of tokens){
  if(token.startsWith('<')){
   const close=token.match(/^<\/([a-z0-9]+)/i),open=token.match(/^<([a-z0-9]+)/i);
   if(open&&open[1].toLowerCase()==='br'){
    breaks++;buf+=token;
    if(breaks>=2&&!stack.length){buf=buf.replace(/(?:<br\s*\/?>\s*){2,}$/i,'');flush();breaks=0;}
    continue;
   }
   breaks=0;buf+=token;
   if(close){const at=stack.lastIndexOf(close[1].toLowerCase());if(at>=0)stack.splice(at);}
   else if(open&&!VOID.has(open[1].toLowerCase())&&!/\/\s*>$/.test(token))stack.push(open[1].toLowerCase());
   if(!stack.length&&sentences>=2)flush();
   continue;
  }
  breaks=0;let pos=0;const re=/[.!?。][”’"')\]」』]*(?:\s+|$)/g;let m;
  while((m=re.exec(token))){
   const end=m.index+m[0].length;
   if(token[m.index]==='.'&&/\d/.test(token[m.index-1]||'')&&/^\d/.test(token.slice(end).trimStart()))continue;
   const piece=token.slice(pos,end);buf+=piece;chars+=piece.replace(/\s+/g,'').length;sentences++;pos=end;
   if(!stack.length&&(sentences>=2||chars>=160))flush();
  }
  const tail=token.slice(pos);buf+=tail;chars+=tail.replace(/\s+/g,'').length;
 }
 flush();return chunks;
}
export function formatReadableHTML(html,{style=true}={}){
 const protectedBlocks=[];
 let result=String(html).replace(/<(script|style)\b[^>]*>[\s\S]*?<\/\1>/gi,whole=>{const key='\uE000READABILITY'+protectedBlocks.length+'\uE001';protectedBlocks.push(whole);return key;});
 result=result.replace(/<p\b([^>]*)>([\s\S]*?)<\/p>/gi,(whole,attrs,inner)=>{
  const chunks=paragraphChunks(inner);if(chunks.length<2)return whole;
  if(/class=["'][^"']*(?:takeaway|tip)[^"']*["']/i.test(attrs))return '<div'+attrs+'>'+chunks.map(s=>'<p>'+s+'</p>').join('\n\n')+'</div>';
  return chunks.map((s,i)=>'<p'+(i?attrs.replace(/\s+id=(?:"[^"]*"|'[^']*')/gi,''):attrs)+'>'+s+'</p>').join('\n\n');
 });
 result=result.replace(/<\/p>\s*(?=<p\b)/gi,'</p>\n\n');
 result=result.replace(/\uE000READABILITY(\d+)\uE001/g,(_,i)=>protectedBlocks[Number(i)]);
 if(style&&!result.includes('data-readability="paragraphs-v1"'))result=result.includes('</head>')?result.replace('</head>',READABILITY_STYLE+'\n</head>'):READABILITY_STYLE+'\n'+result;
 return result;
}
