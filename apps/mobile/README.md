# ATLAS Web Premium

Responsive web command center for ATLAS 1.9, packaged for browser, installable PWA, and Android through Capacitor.

## Current experience

- Command Center with system status and global voice state.
- Searchable module navigation with `Ctrl/⌘ + K` and a complete mobile module drawer.
- Text chat, file upload, browser speech output, and Realtime voice session.
- Live event radar and high-priority event view.
- Research backlog creation, possible-world program summaries, and experiment scoring.
- Ministry overview, council-session preparation, API awareness metrics, My World node creation, hypothesis intake, and mission routing.
- Service worker caches the same-origin app shell and assets for offline reopening; authenticated API data is never cached.

## Local development

```bash
npm install
npm run dev
```

Set `VITE_ATLAS_API_URL` when the API is hosted at a non-default URL. The user must pair the browser or app with an owner code before authenticated features can load.

## Android

```bash
npm run build
npx cap add android
npx cap sync android
cd android && ./gradlew assembleDebug
```

Android microphone permission is added in the APK workflow. Debug APKs are for testing; a release build still needs the project's release-signing policy.
