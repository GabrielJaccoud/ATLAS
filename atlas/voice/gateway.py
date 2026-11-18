from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class VoiceTurn:
    turn_id: str
    input_mode: str
    transcript: str | None
    intent: str | None = None
    attachments: tuple[str, ...] = ()


@dataclass
class VoiceSession:
    session_id: str
    mode: str = "conversational"
    language: str = "pt-BR"
    push_to_talk: bool = True
    allow_interruptions: bool = True
    turns: list[VoiceTurn] = field(default_factory=list)


class VoiceGateway:
    MODES = {"conversational", "research", "briefing", "hands_free", "critical_alert"}

    def open_session(self, session_id: str, *, mode: str = "conversational", language: str = "pt-BR", push_to_talk: bool = True) -> VoiceSession:
        if mode not in self.MODES:
            raise ValueError("Unknown voice mode.")
        return VoiceSession(session_id=session_id, mode=mode, language=language, push_to_talk=push_to_talk)

    def add_turn(self, session: VoiceSession, turn: VoiceTurn) -> VoiceSession:
        session.turns.append(turn)
        return session
