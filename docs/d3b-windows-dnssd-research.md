# D3B Windows DNS-SD lifecycle / observer research

This is public, read-only research only. No live DNS, mDNS, LAN, device, credential, or controller operation occurred.

## Question and decision

The current Windows `DnsServiceBrowse` + `DnsServiceResolve` adapter cannot safely release its `ctypes` callback/request/cancel objects after the first successful resolve callback: Microsoft documents a callback for each result, but does not define terminal-success, post-success cancel, or callback-quiescence semantics. D3B found no released Windows-native alternative that both performs mDNS/DNS-SD observation and supplies the required bounded completion/lifetime contract.

**Decision at D3B: no alternative implementation route was recommended.** D3B ruled out routes that require a documented terminal/quiescence callback before releasing native objects. It did not rule out retaining the existing route's objects for the observer child-process lifetime. A subsequent D3A revalidation adopted that safer ownership boundary: callback, request, cancel handle, event, and first accepted result are retained until child exit; cancellation is never treated as quiescence. D3 remains separately not authorized.

## Route comparison

| Route | Microsoft authority | Completion / cancel contract | D2A / D1 fit | Decision |
| --- | --- | --- | --- | --- |
| A. `DnsServiceBrowse` + `DnsServiceResolve` | Windows 10+ DNS-SD APIs | Browse cancellation has a documented final cancelled callback. Resolve is asynchronous and reports each result, but the published resolve/cancel pages do not define terminal success, cancel-after-success, or quiescence. | D1 shaping is possible. D3A now retains resolve ctypes objects until the D2A child exits, so it does not require undocumented quiescence before release. | No alternative route; process-lifetime ownership selected separately. |
| B1. `DnsQueryEx` + `DnsCancelQuery` | Generic DNS query API | Strongest candidate lifecycle: request result, cancel handle and context remain valid until the single completion callback; cancel does not itself wait, so the callback is the quiescence point. | Parsed DNS records could be bounded and converted without a raw packet parser. | Reject for D3: `DNS_QUERY_MULTICAST_ONLY` is officially LLMNR-only, not mDNS. |
| B2. `DnsStartMulticastQuery` + `DnsStopMulticastQuery` | Windows mDNS request / callback API | Supports mDNS name and record type, but runs indefinitely and invokes callbacks for every response. Stop API supplies no published final-callback or lifetime/quiescence rule. | PTR/SRV/TXT could in principle shape to D1, but direct-child cleanup has the same unresolved callback-lifetime risk. | Reject pending authority. |
| B3. `DnsQueryRaw` + `DnsCancelQueryRaw` | Generic raw-query API, marked prerelease in Microsoft docs | Cancellation callback semantics are explicit, but the API exposes raw packet material and Microsoft does not establish it as the required mDNS DNS-SD path. | Would violate this project’s no raw DNS/mDNS parser boundary. | Reject. |
| C. `Resolve-DnsName` / built-in executable | PowerShell DNS client documentation | Cmdlet documents DNS with LLMNR/NetBIOS options; no mDNS DNS-SD browse/resolve contract. No Microsoft-documented built-in `dns-sd` observer was found; this host has no such executable. | Not a safe DNS-SD observer. | Reject. |

## Primary evidence

- [DnsServiceResolve](https://learn.microsoft.com/en-us/windows/win32/api/windns/nf-windns-dnsserviceresolve): asynchronous; callback is invoked for each result; cancel handle remains valid until query cancellation. It does not define success terminality.
- [DnsServiceResolveCancel](https://learn.microsoft.com/en-us/windows/win32/api/windns/nf-windns-dnsserviceresolvecancel): cancels a running resolve but has no published final-callback or quiescence rule.
- [DnsQueryEx](https://learn.microsoft.com/en-us/windows/win32/api/windns/nf-windns-dnsqueryex) and [DnsCancelQuery](https://learn.microsoft.com/en-us/windows/win32/api/windns/nf-windns-dnscancelquery): explicitly retain async query state until the completion callback; `DnsCancelQuery` requires tracking that callback.
- [DNS query constants](https://learn.microsoft.com/en-us/windows/win32/dns/dns-constants): `DNS_QUERY_MULTICAST_ONLY` uses only LLMNR.
- [MDNS_QUERY_REQUEST](https://learn.microsoft.com/en-us/windows/win32/api/windns/ns-windns-mdns_query_request), [DnsStartMulticastQuery](https://learn.microsoft.com/en-us/windows/win32/api/windns/nf-windns-dnsstartmulticastquery), and [DnsStopMulticastQuery](https://learn.microsoft.com/en-us/windows/win32/api/windns/nf-windns-dnsstopmulticastquery): mDNS query capability exists, but the query runs indefinitely and published stop semantics do not provide quiescence.
- [Resolve-DnsName](https://learn.microsoft.com/en-us/powershell/module/dnsclient/resolve-dnsname): supports DNS and explicit LLMNR/NetBIOS modes; no mDNS DNS-SD browse/resolve mode is documented.

The local Windows SDK `10.0.26100.0` `WinDNS.h` exposes the same route families. Its `MDNS_QUERY_REQUEST.ulRefCount` comment is not a usable lifecycle contract because the public structure documentation marks that member reserved/do-not-use.

## Historical unblock condition

The following was the D3B condition for an implementation that releases resolve state before process exit. It has been superseded for D3A by process-lifetime ownership, not satisfied by new terminal-success authority:

1. authoritative Microsoft SDK/API text that specifies `DnsServiceResolve` terminal-success and post-cancel callback lifetime; or
2. authoritative Microsoft stop/quiescence semantics for `DnsStartMulticastQuery`; or
3. separate explicit authorization for a bounded platform proof that establishes one of those contracts without performing live LAN observation.

Do not substitute a raw packet parser, third-party mDNS stack, fixed delay, or inferred cancellation behavior. D3 itself still requires a separate explicit live-observation authorization.
