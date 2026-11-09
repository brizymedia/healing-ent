export const EMPHASIS_STYLE = "<style data-emphasis=\"key-points-v1\">.body h2,main .sbody h2{font-size:clamp(1.35rem,2.1vw,1.6rem);line-height:1.5;font-weight:800;color:#173f78;border-left:4px solid #2d64bd;padding-left:.75rem;margin-top:2.1rem}.body h3,.faq h3,main .sbody h3{font-size:1.1rem;line-height:1.55;font-weight:800;color:#24415f}.body b,.body strong{font-weight:800;color:#174da1}.points{background:#f0f5ff;border:1px solid #c9d9f4;border-left:5px solid #2d64bd;border-radius:12px;padding:1.15rem 1.3rem}.points>b:first-child{display:block;font-size:1.15rem;font-weight:800;color:#173f78;margin-bottom:.6rem}.points li{font-weight:600;color:#24415f;margin:.5em 0}.case-story .takeaway,.body .tip{background:#eef4ff;border:1px solid #c9d9f4;border-left:4px solid #2d64bd;border-radius:12px;padding:1.1rem 1.25rem}.case-story .takeaway>p:first-child{font-size:1.065em;font-weight:750;color:#173f78}.case-story .takeaway>p:first-child strong{font-weight:850;color:#174da1}.case-story .takeaway>p:not(:first-child){font-weight:400;color:#243447}main .sbody>p:first-of-type{font-size:1.06em;font-weight:650;color:#24415f}.nowon-story blockquote{background:#f0f5ff;border-left-color:#2d64bd}.body thead th,main .sbody th{background:#edf3ff;color:#173f78;font-weight:800}@media(max-width:640px){.body h2,main .sbody h2{font-size:1.3rem;border-left-width:3px;padding-left:.6rem}.points,.case-story .takeaway,.body .tip{padding:1rem}.case-story .takeaway>p:first-child{font-size:1.035em}}</style>";
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
 if(style&&!result.includes('data-emphasis="key-points-v1"'))result=result.includes('</head>')?result.replace('</head>',EMPHASIS_STYLE+'\n</head>'):EMPHASIS_STYLE+'\n'+result;
 return result;
}
