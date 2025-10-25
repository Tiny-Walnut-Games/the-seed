from __future__ import annotations
from typing import List, Dict, Any, Optional
import requests
import json
import time
from .audio import TTSProvider, TTSProviderFactory, VoiceConfig, VoiceCharacteristic, TTSRequest


class LLMClient:
    """Universal LLM client supporting multiple backends (vLLM, Ollama, OpenAI)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.backend_type = self.config.get("backend", "auto")  # auto, vllm, ollama, openai
        self.endpoints = self._get_endpoints()
        self.current_endpoint = None
        self.model_name = None
        self._initialized = False

    def _get_endpoints(self) -> List[str]:
        """Get available LLM endpoints based on configuration."""
        if self.backend_type == "vllm":
            return [
                f"http://localhost:{port}/v1"
                for port in [8500, 8300, 8100, 8700]  # QA, Edit, Fast, Plan models
            ]
        elif self.backend_type == "ollama":
            return ["http://localhost:11434/api"]
        elif self.backend_type == "openai":
            return ["https://api.openai.com/v1"]
        else:  # auto
            # Try vLLM first, then Ollama
            return [
                f"http://localhost:{port}/v1"
                for port in [8500, 8300, 8100, 8700]
            ] + ["http://localhost:11434/api"]

    def _test_endpoint(self, endpoint: str) -> bool:
        """Test if an endpoint is available."""
        try:
            if "/api" in endpoint:  # Ollama
                response = requests.get(f"{endpoint}/tags", timeout=2)
            else:  # OpenAI-compatible (vLLM)
                response = requests.get(f"{endpoint}/models", timeout=2)
            return response.status_code == 200
        except:
            return False

    def _get_available_endpoint(self) -> Optional[str]:
        """Find first available endpoint."""
        for endpoint in self.endpoints:
            if self._test_endpoint(endpoint):
                return endpoint
        return None

    def _initialize(self) -> bool:
        """Initialize the client with an available endpoint."""
        if self._initialized:
            return True

        endpoint = self._get_available_endpoint()
        if not endpoint:
            print("⚠️ No LLM endpoints available")
            return False

        self.current_endpoint = endpoint

        # Detect model
        if "/api" in endpoint:  # Ollama
            try:
                response = requests.get(f"{endpoint}/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    if models:
                        self.model_name = models[0]["name"]
                        print(f"🤖 Connected to Ollama: {self.model_name}")
            except:
                pass
        else:  # OpenAI-compatible (vLLM)
            try:
                response = requests.get(f"{endpoint}/models", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("data", [])
                    if models:
                        self.model_name = models[0]["id"]
                        print(f"🤖 Connected to vLLM: {self.model_name}")
            except:
                pass

        self._initialized = True
        return True

    def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate response from LLM."""
        if not self._initialize():
            return self._mock_response(prompt, context)

        start_time = time.time()

        try:
            if "/api" in self.current_endpoint:  # Ollama
                response = self._call_ollama(prompt, context)
            else:  # OpenAI-compatible (vLLM)
                response = self._call_openai_compatible(prompt, context)

            generation_time = (time.time() - start_time) * 1000

            return {
                "response_text": response.get("content", response.get("text", "")),
                "confidence": self._extract_confidence(response),
                "voice_contributions": self._extract_voice_contributions(context),
                "generation_time_ms": generation_time,
                "model_used": self.model_name,
                "endpoint": self.current_endpoint,
                "success": True
            }

        except Exception as e:
            print(f"⚠️ LLM generation failed: {e}")
            return self._mock_response(prompt, context)

    def _call_ollama(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Call Ollama API."""
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 500
            }
        }

        response = requests.post(
            f"{self.current_endpoint}/generate",
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def _call_openai_compatible(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Call OpenAI-compatible API (vLLM)."""
        # Convert prompt to chat format
        messages = [{"role": "user", "content": prompt}]

        # Add context as system message if available
        if context:
            context_str = self._format_context(context)
            if context_str:
                messages.insert(0, {"role": "system", "content": context_str})

        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500,
            "stream": False
        }

        headers = {"Content-Type": "application/json"}
        if self.config.get("api_key"):
            headers["Authorization"] = f"Bearer {self.config['api_key']}"

        response = requests.post(
            f"{self.current_endpoint}/chat/completions",
            json=data,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for LLM consumption."""
        if not context:
            return ""

        parts = []

        # Add voices context
        voices = context.get("voices", [])
        if voices:
            parts.append("Available Perspectives:")
            for voice in voices:
                parts.append(f"- {voice.get('perspective', 'Unknown perspective')}")

        # Add mist context
        mist_context = context.get("mist_context", [])
        if mist_context:
            parts.append("Recent Thoughts:")
            for mist in mist_context[:3]:  # Limit to avoid context overflow
                if mist.strip():
                    parts.append(f"- {mist}")

        # Add generation mode
        mode = context.get("generation_mode", "")
        if mode:
            parts.append(f"Generation Mode: {mode}")

        return "\n".join(parts)

    def _extract_confidence(self, response: Dict[str, Any]) -> float:
        """Extract confidence score from response."""
        # Try to extract from response metadata
        if "done_reason" in response:  # Ollama
            return 0.8 if response.get("done_reason") == "stop" else 0.6
        elif "finish_reason" in str(response):  # OpenAI-compatible
            return 0.8 if "stop" in str(response) else 0.6

        # Default confidence based on response length
        content = response.get("content", response.get("text", ""))
        if len(content) > 100:
            return 0.8
        elif len(content) > 50:
            return 0.7
        else:
            return 0.6

    def _extract_voice_contributions(self, context: Optional[Dict[str, Any]]) -> List[str]:
        """Extract voice contributions from context."""
        if not context:
            return []

        voices = context.get("voices", [])
        return [voice.get("voice_id", f"voice_{i}") for i, voice in enumerate(voices[:3])]

    def _mock_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fallback mock response when no LLM is available."""
        voices = context.get("voices", []) if context else []
        voice_count = len(voices)

        mock_text = f"[Mock response from {voice_count} cognitive voices] "
        mock_text += "I understand your request and would provide a thoughtful response "
        mock_text += "based on the available perspectives and context."

        return {
            "response_text": mock_text,
            "confidence": 0.5,
            "voice_contributions": [v.get("voice_id", f"voice_{i}") for i, v in enumerate(voices[:2])],
            "generation_time_ms": 50,
            "model_used": "mock",
            "endpoint": "none",
            "success": False
        }


class Selector:
    """Selector: assembles prompt (multi-voice scaffold) with real LLM integration."""
    def __init__(self, castle_graph, cloud_store, governance=None, tts_provider: Optional[TTSProvider] = None, llm_config: Optional[Dict[str, Any]] = None):
        self.castle_graph = castle_graph
        self.cloud_store = cloud_store
        self.governance = governance

        # LLM integration
        self.llm_client = LLMClient(llm_config)

        # v0.5 Multimodal: TTS integration
        self.tts_provider = tts_provider or TTSProviderFactory.create_best_available()
        self.voice_mapping = self._create_voice_mapping()
        self.tts_enabled = False  # Can be enabled for audio output

    def assemble_prompt(self, context: str = "", limit: int = 3) -> Dict[str, Any]:
        """Assemble multi-voice prompt from castle rooms and mist lines with advanced engineering."""
        top_rooms = self.castle_graph.get_top_rooms(limit)
        active_mist = self.cloud_store.get_active_mist(limit)

        # Advanced prompt engineering with voice modulation
        voices = []
        voice_weights = []

        for i, room in enumerate(top_rooms):
            # Calculate voice weight based on heat and recency
            heat_weight = room["heat"]
            recency_weight = 1.0 / (1.0 + room.get("age_hours", 0))  # Newer rooms get higher weight
            combined_weight = (heat_weight * 0.7 + recency_weight * 0.3)

            voice = {
                "voice_id": f"voice_{room['concept_id']}",
                "heat_level": room["heat"],
                "perspective": self._generate_perspective(room),
                "weight": combined_weight,
                "concept": room["concept_id"].replace("concept_", ""),
                "specialization": self._determine_voice_specialization(room),
                "modulation": self._calculate_voice_modulation(room, i),
            }
            voices.append(voice)
            voice_weights.append(combined_weight)

        # Normalize voice weights
        if voice_weights:
            total_weight = sum(voice_weights)
            voice_weights = [w / total_weight for w in voice_weights]
            for i, voice in enumerate(voices):
                voice["normalized_weight"] = voice_weights[i]

        # Enhanced mist context processing
        processed_mist = self._process_mist_context(active_mist)

        # Calculate prompt complexity and style
        prompt_complexity = self._calculate_prompt_complexity(voices, processed_mist)
        generation_style = self._determine_generation_style(prompt_complexity, context)

        prompt_scaffold = {
            "context": context,
            "voices": voices,
            "mist_context": processed_mist,
            "generation_mode": self.cloud_store.generation_mode,
            "humidity_index": self.cloud_store.humidity_index,
            "prompt_complexity": prompt_complexity,
            "generation_style": generation_style,
            "voice_count": len(voices),
            "total_weight": sum(voice_weights),
            "engineered_at": time.time(),
        }

        return prompt_scaffold

    def respond(self, prompt_scaffold: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response using real LLM integration with advanced prompt engineering."""
        # Construct enhanced prompt for LLM
        enhanced_prompt = self._construct_enhanced_prompt(prompt_scaffold)

        # Generate response using LLM client
        llm_response = self.llm_client.generate_response(enhanced_prompt, prompt_scaffold)

        # Post-process response based on voice contributions
        processed_response = self._post_process_response(llm_response, prompt_scaffold)

        # Apply governance if available
        if self.governance:
            processed_response = self.governance.filter_response(processed_response)

        # Add metadata about the generation process
        processed_response["prompt_metadata"] = {
            "voice_count": prompt_scaffold.get("voice_count", 0),
            "complexity": prompt_scaffold.get("prompt_complexity", "medium"),
            "style": prompt_scaffold.get("generation_style", "balanced"),
            "humidity": prompt_scaffold.get("humidity_index", 0.5),
        }

        return processed_response

    def enable_tts(self, enabled: bool = True):
        """Enable or disable TTS output."""
        self.tts_enabled = enabled and self.tts_provider.is_available()
        if self.tts_enabled:
            print("🗣️ TTS Output: Enabled")
        else:
            print("🔇 TTS Output: Disabled")

    def _create_voice_mapping(self) -> Dict[str, VoiceConfig]:
        """Create mapping from cognitive concepts to TTS voices."""
        available_voices = self.tts_provider.get_available_voices()

        # Create smart mapping based on voice characteristics
        mapping = {}
        for voice in available_voices:
            if voice.characteristic == VoiceCharacteristic.NARRATOR:
                mapping["default"] = voice
                mapping["concept_implementing"] = voice
            elif voice.characteristic == VoiceCharacteristic.EXPLORER:
                mapping["concept_advanced"] = voice
                mapping["concept_debugging"] = voice
            elif voice.characteristic == VoiceCharacteristic.SCHOLAR:
                mapping["concept_memory"] = voice
                mapping["concept_semantic"] = voice
            elif voice.characteristic == VoiceCharacteristic.ADVISOR:
                mapping["concept_wisdom"] = voice
                mapping["concept_governance"] = voice
            elif voice.characteristic == VoiceCharacteristic.ALERT:
                mapping["concept_conflict"] = voice
                mapping["concept_urgent"] = voice

        # Ensure default voice exists
        if "default" not in mapping and available_voices:
            mapping["default"] = available_voices[0]

        return mapping

    def _get_voice_for_concept(self, concept_id: str) -> VoiceConfig:
        """Get appropriate TTS voice for a concept."""
        # Try exact match first
        if concept_id in self.voice_mapping:
            return self.voice_mapping[concept_id]

        # Try partial matches for concept patterns
        for mapped_concept, voice in self.voice_mapping.items():
            if mapped_concept in concept_id or concept_id in mapped_concept:
                return voice

        # Fall back to default
        return self.voice_mapping.get("default", self.tts_provider.get_available_voices()[0])

    def synthesize_response(self, response_text: str, primary_voice_id: str = None) -> Optional[str]:
        """Synthesize response text to speech using appropriate voice."""
        if not self.tts_enabled or not response_text.strip():
            return None

        # Determine voice
        if primary_voice_id:
            voice_config = self._get_voice_for_concept(primary_voice_id)
        else:
            voice_config = self.voice_mapping.get("default")

        if not voice_config:
            return None

        # Create TTS request
        tts_request = TTSRequest(
            text=response_text,
            voice_config=voice_config,
            context={"source": "cognitive_response", "voice_id": primary_voice_id}
        )

        # Synthesize
        result = self.tts_provider.synthesize(tts_request)

        if result.success:
            return f"TTS synthesized: {result.duration_ms}ms using {voice_config.name}"
        else:
            print(f"TTS failed: {result.error_message}")
            return None

    def _generate_perspective(self, room: Dict[str, Any]) -> str:
        """Generate rich voice perspective from castle room data."""
        # Rich perspective generation based on room history
        concept = room["concept_id"].replace("concept_", "")
        heat = room["heat"]
        age = room.get("age_hours", 0)

        # Base perspective from heat
        if heat > 0.7:
            base_perspective = f"Passionate expert and advocate for {concept}"
        elif heat > 0.4:
            base_perspective = f"Knowledgeable practitioner of {concept}"
        elif heat > 0.2:
            base_perspective = f"Interested learner exploring {concept}"
        else:
            base_perspective = f"Curious observer of {concept}"

        # Add temporal context
        if age < 1:
            temporal_context = " (recently activated)"
        elif age < 24:
            temporal_context = " (actively developing)"
        else:
            temporal_context = " (well-established)"

        # Add specialization hints
        specialization = self._determine_voice_specialization(room)
        if specialization:
            specialization_text = f", specializing in {specialization}"
        else:
            specialization_text = ""

        return f"{base_perspective}{temporal_context}{specialization_text}"

    def _determine_voice_specialization(self, room: Dict[str, Any]) -> str:
        """Determine voice specialization based on concept and metadata."""
        concept = room["concept_id"].lower()

        if "implement" in concept or "code" in concept:
            return "practical implementation"
        elif "debug" in concept or "conflict" in concept:
            return "problem-solving"
        elif "memory" in concept or "semantic" in concept:
            return "knowledge organization"
        elif "wisdom" in concept or "governance" in concept:
            return "strategic thinking"
        elif "advanced" in concept or "explor" in concept:
            return "innovation and discovery"
        else:
            return ""

    def _calculate_voice_modulation(self, room: Dict[str, Any], index: int) -> Dict[str, float]:
        """Calculate voice modulation parameters."""
        heat = room["heat"]

        # Modulate based on heat and position
        intensity = 0.5 + heat * 0.5  # 0.5 to 1.0
        pitch = 0.8 + (index * 0.1)  # Slight variation between voices
        tempo = 0.9 + heat * 0.2  # Faster for higher heat

        return {
            "intensity": intensity,
            "pitch": pitch,
            "tempo": tempo,
            "emphasis": heat  # Higher heat = more emphasis
        }

    def _process_mist_context(self, active_mist: List[Dict[str, Any]]) -> List[str]:
        """Process and enhance mist context."""
        processed = []

        for mist in active_mist:
            proto_thought = mist.get("proto_thought", "").strip()
            if proto_thought:
                # Add metadata to mist context
                enhanced = proto_thought
                if mist.get("affect"):
                    enhanced += f" [affect: {mist['affect']}]"
                if mist.get("confidence"):
                    enhanced += f" [confidence: {mist['confidence']:.2f}]"
                processed.append(enhanced)

        return processed

    def _calculate_prompt_complexity(self, voices: List[Dict[str, Any]], mist_context: List[str]) -> str:
        """Calculate overall prompt complexity."""
        voice_complexity = len(voices)
        mist_complexity = len(mist_context)
        heat_complexity = sum(v.get("heat_level", 0) for v in voices) / len(voices) if voices else 0

        total_score = voice_complexity * 2 + mist_complexity + heat_complexity * 3

        if total_score > 8:
            return "high"
        elif total_score > 4:
            return "medium"
        else:
            return "low"

    def _determine_generation_style(self, complexity: str, context: str) -> str:
        """Determine optimal generation style based on complexity and context."""
        context_lower = context.lower()

        if "question" in context_lower or "help" in context_lower:
            return "responsive"
        elif "create" in context_lower or "generate" in context_lower:
            return "creative"
        elif "analyze" in context_lower or "explain" in context_lower:
            return "analytical"
        elif complexity == "high":
            return "integrative"
        elif complexity == "low":
            return "focused"
        else:
            return "balanced"

    def _construct_enhanced_prompt(self, prompt_scaffold: Dict[str, Any]) -> str:
        """Construct enhanced prompt for LLM consumption."""
        context = prompt_scaffold.get("context", "")
        voices = prompt_scaffold.get("voices", [])
        mist_context = prompt_scaffold.get("mist_context", [])
        complexity = prompt_scaffold.get("prompt_complexity", "medium")
        style = prompt_scaffold.get("generation_style", "balanced")

        # Build prompt sections
        prompt_parts = []

        # System instruction based on style
        style_instructions = {
            "responsive": "Provide a helpful, direct response to the query.",
            "creative": "Generate innovative and imaginative content.",
            "analytical": "Provide detailed analysis and explanation.",
            "integrative": "Synthesize multiple perspectives into a coherent response.",
            "focused": "Provide a concise, targeted response.",
            "balanced": "Provide a well-rounded, thoughtful response."
        }

        prompt_parts.append(f"Style: {style_instructions.get(style, style_instructions['balanced'])}")

        # Add voice perspectives
        if voices:
            prompt_parts.append("\nAvailable Perspectives:")
            for voice in voices:
                weight = voice.get("normalized_weight", 0.0)
                perspective = voice.get("perspective", "Unknown perspective")
                prompt_parts.append(f"- {perspective} (influence: {weight:.2f})")

        # Add mist context
        if mist_context:
            prompt_parts.append("\nRecent Thoughts & Context:")
            for mist in mist_context[:5]:  # Limit to avoid overflow
                prompt_parts.append(f"- {mist}")

        # Add complexity guidance
        complexity_guidance = {
            "high": "Consider all perspectives and integrate them into a comprehensive response.",
            "medium": "Balance multiple perspectives while maintaining clarity.",
            "low": "Focus on the most relevant perspective for a clear response."
        }

        prompt_parts.append(f"\nGuidance: {complexity_guidance.get(complexity, complexity_guidance['medium'])}")

        # Add the main context/query
        if context:
            prompt_parts.append(f"\nQuery/Context: {context}")

        return "\n".join(prompt_parts)

    def _post_process_response(self, llm_response: Dict[str, Any], prompt_scaffold: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process LLM response based on prompt context."""
        response_text = llm_response.get("response_text", "")
        voices = prompt_scaffold.get("voices", [])

        # Enhance response with voice attribution
        if voices and len(voices) > 1:
            # Add subtle voice attribution hints
            voice_names = [v.get("concept", "voice") for v in voices[:3]]
            attribution = f"\n\n[Synthesized from perspectives: {', '.join(voice_names)}]"
            response_text += attribution

        # Adjust confidence based on response quality
        base_confidence = llm_response.get("confidence", 0.5)
        length_factor = min(len(response_text) / 200, 1.0)  # Longer responses get slight confidence boost
        adjusted_confidence = min(base_confidence + length_factor * 0.1, 1.0)

        # Create enhanced response
        enhanced_response = llm_response.copy()
        enhanced_response.update({
            "response_text": response_text,
            "confidence": adjusted_confidence,
            "post_processed": True,
            "voice_count": len(voices),
            "response_length": len(response_text)
        })

        return enhanced_response
