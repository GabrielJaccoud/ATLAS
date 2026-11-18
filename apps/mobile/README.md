# ATLAS Web 2.0

Luxury Intelligence Command Center with a responsive WebGL 3D layer. The browser experience is the primary product; the PWA and Capacitor Android package use the same interface.

## Experience

- **Atlas Core:** interactive three dimensional nucleus with restrained gold, blue, and cyan light; responds to voice, research, alert, and critical states.
- **Possible Worlds:** spatial model constellation paired with explicit probability values and experiment recommendations.
- **My World:** three dimensional view of the saved knowledge graph, alongside its readable node and relationship records.
- **Operations:** dynamic Home, Radar, Urgent, Science, Research, Ministries, Council, Awareness, Innovation, and Actions.
- **Talk:** text, file upload, speech output, and Realtime voice session.
- **Navigation:** responsive desktop rail, complete mobile drawer, and module search with `Ctrl/⌘ + K`.
- **PWA:** shell and same-origin assets may reopen offline. Authenticated API responses are not cached.
- **Accessibility/performance:** reduced-motion support, API fallback visuals when WebGL is unavailable, render resolution capped for mobile GPUs, and animation pauses while the document is hidden.

## Local development

```bash
npm install
npm run dev
```

Set `VITE_ATLAS_API_URL` to the API endpoint. The API remains version 1.9 while the web product is version 2.0; pair the browser with an owner code to load private data.

## Android package

```bash
npm run build
npx cap add android
npx cap sync android
cd android && ./gradlew assembleDebug
```

The Android workflow adds microphone permission for Realtime voice. Debug APKs are for testing; release distribution requires the project's release-signing policy.
