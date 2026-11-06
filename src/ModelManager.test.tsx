// @vitest-environment jsdom
import {render,screen,within,cleanup,waitFor} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {it,expect,vi,afterEach} from 'vitest';
import {ModelManager} from './ModelManager';
import {setLanguage} from './i18n';
afterEach(()=>{cleanup();vi.unstubAllGlobals();setLanguage('de')});
it('explains custom adapter requirements, gates selection and confirms deletion in app style',async()=>{
 setLanguage('en');let models:any[]=[];const calls:any[]=[];
 vi.stubGlobal('fetch',vi.fn(async(url,init)=>{const body=init?.body?JSON.parse(init.body):null;calls.push({url:String(url),body});if(String(url).endsWith('/custom'))models=[{id:'custom-authored',name:'example/authored',purpose:'audio',description:'Authored compatible fixture',download:'1 GB',memory:'RAM',custom:true,installed:false,active:false,revision:'abcdef12'}];if(String(url).endsWith('/delete'))models=[];return new Response(JSON.stringify({models}),{status:200})}));
 render(<ModelManager busy={false} perform={async f=>f()} job={async()=>{models[0].installed=true}}/>);
 await userEvent.click(screen.getByText('Add a custom model'));
 await userEvent.selectOptions(screen.getByLabelText('Model purpose'),'audio');
 expect(screen.getByText(/generic language model is not compatible/)).toBeTruthy();
 await userEvent.type(screen.getByLabelText('Model link'),'https://huggingface.co/example/authored');
 await userEvent.click(screen.getByRole('button',{name:'Check link and add'}));
 await screen.findByRole('heading',{name:'example/authored'});
 expect(calls.find(c=>c.url.endsWith('/custom')).body.purpose).toBe('audio');
 expect(screen.getByRole('button',{name:'Select'}).hasAttribute('disabled')).toBe(true);
 await userEvent.click(screen.getByRole('button',{name:'Download'}));
 await waitFor(()=>expect(screen.getByRole('button',{name:'Select'}).hasAttribute('disabled')).toBe(false));
 await userEvent.click(screen.getByRole('button',{name:'Remove'}));
 expect(calls.some(c=>c.url.endsWith('/delete'))).toBe(false);
 await userEvent.click(within(screen.getByRole('alertdialog')).getByRole('button',{name:'Cancel'}));
 expect(screen.getByRole('heading',{name:'example/authored'})).toBeTruthy();
 await userEvent.click(screen.getByRole('button',{name:'Remove'}));
 await userEvent.click(within(screen.getByRole('alertdialog')).getByRole('button',{name:'Remove model'}));
 await waitFor(()=>expect(screen.queryByRole('heading',{name:'example/authored'})).toBeNull());
});
