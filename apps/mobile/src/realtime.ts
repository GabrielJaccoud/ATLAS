import { atlasFetch } from "./api";

export type RealtimeHandle = {
  peer: RTCPeerConnection;
  channel: RTCDataChannel;
  media: MediaStream;
  stop: () => void;
};

export async function startRealtimeVoice(
  onEvent?: (event: any) => void,
): Promise<RealtimeHandle> {
  const token = await atlasFetch<{ value: string }>("/voice/realtime-token", {
    method: "POST",
  });

  const peer = new RTCPeerConnection();
  const remoteAudio = document.createElement("audio");
  remoteAudio.autoplay = true;
  peer.ontrack = (event) => {
    remoteAudio.srcObject = event.streams[0];
  };

  const media = await navigator.mediaDevices.getUserMedia({ audio: true });
  media.getTracks().forEach((track) => peer.addTrack(track, media));

  const channel = peer.createDataChannel("oai-events");
  channel.onmessage = (event) => {
    try {
      onEvent?.(JSON.parse(event.data));
    } catch {
      onEvent?.({ type: "raw", data: event.data });
    }
  };

  const offer = await peer.createOffer();
  await peer.setLocalDescription(offer);

  const response = await fetch("https://api.openai.com/v1/realtime/calls", {
    method: "POST",
    body: offer.sdp,
    headers: {
      Authorization: `Bearer ${token.value}`,
      "Content-Type": "application/sdp",
    },
  });
  if (!response.ok) {
    throw new Error(`Realtime connection failed: ${response.status} ${await response.text()}`);
  }

  const answer = await response.text();
  await peer.setRemoteDescription({ type: "answer", sdp: answer });

  return {
    peer,
    channel,
    media,
    stop: () => {
      channel.close();
      media.getTracks().forEach((track) => track.stop());
      peer.close();
    },
  };
}
