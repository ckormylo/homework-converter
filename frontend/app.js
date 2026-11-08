// Replace this placeholder after deploying the backend. Never expose OPENAI_API_KEY here.
const API_URL = 'REPLACE_WITH_RENDER_URL';
const fileInput=document.querySelector('#file'),button=document.querySelector('#convert'),status=document.querySelector('#status'),label=document.querySelector('#fileLabel'),result=document.querySelector('#result'),reviewEl=document.querySelector('#review'),drop=document.querySelector('#drop');
let blobUrl=null;
function selected(file){if(!file)return;label.textContent=file.name;const ok=file.name.toLowerCase().endsWith('.pdf')&&file.size<=8*1024*1024;button.disabled=!ok;status.textContent=ok?'':'Choose a PDF under 8 MB.';result.hidden=true}
fileInput.addEventListener('change',()=>selected(fileInput.files[0]));
drop.addEventListener('dragover',e=>{e.preventDefault();drop.classList.add('drag')});
drop.addEventListener('dragleave',()=>drop.classList.remove('drag'));
drop.addEventListener('drop',e=>{e.preventDefault();drop.classList.remove('drag');if(e.dataTransfer.files.length){fileInput.files=e.dataTransfer.files;selected(fileInput.files[0])}});
function pdfBlob(b64){const bytes=atob(b64),chunks=[];for(let i=0;i<bytes.length;i+=8192){const s=bytes.slice(i,i+8192),a=new Uint8Array(s.length);for(let j=0;j<s.length;j++)a[j]=s.charCodeAt(j);chunks.push(a)}return new Blob(chunks,{type:'application/pdf'})}
button.addEventListener('click',async()=>{
 if(!fileInput.files[0])return;
 if(API_URL.includes('REPLACE_WITH')){status.textContent='The administrator must configure the backend URL before conversion can work.';return}
 const data=new FormData();data.append('file',fileInput.files[0]);data.append('problems_per_page',document.querySelector('#problems').value);data.append('font_pt',document.querySelector('#font').value);data.append('page_color',document.querySelector('#color').value);data.append('highlight',document.querySelector('#highlight').checked);data.append('simplify',document.querySelector('#simplify').checked);
 button.disabled=true;result.hidden=true;status.textContent='Analyzing, adapting and checking your worksheet…';
 try{const response=await fetch(API_URL+'/convert',{method:'POST',body:data});if(!response.ok){let msg='Unable to convert this worksheet.';try{msg=(await response.json()).detail||msg}catch{}throw Error(msg)}
 const out=await response.json();if(blobUrl)URL.revokeObjectURL(blobUrl);blobUrl=URL.createObjectURL(pdfBlob(out.pdf_base64));document.querySelector('#download').href=blobUrl;document.querySelector('#preview').href=blobUrl;
 const check=out.review||{passed:false,warnings:['Review unavailable']};reviewEl.replaceChildren();const div=document.createElement('div');div.className=check.passed?'success':'warning';const h=document.createElement('strong');h.textContent=check.passed?'Automated review passed':'Teacher review required';div.append(h);const p=document.createElement('p');p.textContent=(check.question_count||'?')+' problems identified. Please compare the PDF with the original.';div.append(p);if(check.warnings?.length){const ul=document.createElement('ul');for(const warning of check.warnings){const li=document.createElement('li');li.textContent=warning;ul.append(li)}div.append(ul)}reviewEl.append(div);result.hidden=false;status.textContent='Conversion complete.'}
 catch(error){status.textContent=error.message||'Conversion failed.'}finally{button.disabled=false}
});
