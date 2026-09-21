# Palestine Banner

> A free HTML banner in support of freedom, dignity, and justice for Palestinians.

Canonical page: https://palestinebanner.com/

Author: [Nadim Kobeissi](https://nadim.computer).

## What it does

Add the banner to the top of your website. It has a black background, green text, and an inline Palestinian flag. The message is:

Freedom, dignity, and justice for Palestinians.

The banner links to https://palestinebanner.com/click, which leads to the [donation options page](https://palestinebanner.com/click/). Visitors choose an organization and donate directly on its official website.

## Add the banner

Paste this immediately after your opening `<body>` tag, or into an HTML block at the top of your page. It needs no JavaScript, external files, or tracking. It is free to use and adapt.

```html
<a href="https://palestinebanner.com/click" style="
  box-sizing:border-box;display:flex;align-items:center;
  justify-content:center;gap:12px;width:100%;padding:15px 20px;
  background:#000;color:#75e39b;text-decoration:none;text-align:center;
  font:600 14px/1.5 system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="16"
    viewBox="0 0 60 30" aria-hidden="true"
    style="display:block;flex-shrink:0;outline:1px solid #ffffff30;">
    <path fill="#000" d="M0 0h60v10H0z"/>
    <path fill="#fff" d="M0 10h60v10H0z"/>
    <path fill="#149454" d="M0 20h60v10H0z"/>
    <path fill="#e6443f" d="m0 0 30 15L0 30z"/>
  </svg>
  <span>Freedom, dignity, and justice for Palestinians.</span>
  <span aria-hidden="true" style="flex-shrink:0;">&#8599;</span>
</a>
```

[Download the HTML snippet](https://palestinebanner.com/downloads/banner.html).
