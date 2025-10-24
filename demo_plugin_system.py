#!/usr/bin/env python3
"""
Warbler/Faculty Engine Plugin System Demo - Cognitive Geo-Thermal Lore Engine v0.9

Demonstrates the plugin architecture with sentiment analysis and discourse tracking
working together to provide enhanced cognitive event processing.

🧙‍♂️ "Behold the power of modular cognitive enhancement!" - Bootstrap Sentinel
"""

import sys
import os
import time
import json
from pathlib import Path

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent / "engine"))

from engine.plugins.plugin_manager import PluginManager
from engine.plugins.manifest_loader import ManifestLoader
from engine.plugins.examples.sentiment_lens.plugin import SentimentLensPlugin
from engine.plugins.examples.discourse_tracker.plugin import DiscourseTrackerPlugin
from engine.audio_event_bus import AudioEventBus, AudioEvent, AudioEventType


def create_metadata_from_manifest(manifest_loader, manifest_path):
    """Helper to create PluginMetadata from manifest file."""
    from engine.plugins.base_plugin import PluginMetadata, PluginCapability

    manifest_data = manifest_loader.load_manifest(manifest_path)

    # Convert string capabilities to enum
    capabilities = set()
    for cap_str in manifest_data.get("capabilities", []):
        try:
            capabilities.add(PluginCapability(cap_str))
        except ValueError:
            print(f"Warning: Unknown capability '{cap_str}' ignored")

    # Convert string event types to enum
    event_subscriptions = set()
    for event_str in manifest_data.get("event_subscriptions", []):
        try:
            event_subscriptions.add(AudioEventType(event_str))
        except ValueError:
            print(f"Warning: Unknown event type '{event_str}' ignored")

    return PluginMetadata(
        name=manifest_data["name"],
        version=manifest_data["version"],
        author=manifest_data["author"],
        description=manifest_data["description"],
        capabilities=capabilities,
        dependencies=manifest_data.get("dependencies", []),
        min_engine_version=manifest_data.get("min_engine_version", "0.9.0"),
        max_memory_mb=manifest_data.get("max_memory_mb", 50),
        max_execution_time_ms=manifest_data.get("max_execution_time_ms", 1000),
        event_subscriptions=event_subscriptions
    )


def print_separator(title=""):
    """Print a decorative separator."""
    print("\n" + "="*60)
    if title:
        print(f"  {title}")
        print("="*60)
    print()


def demo_plugin_loading():
    """Demonstrate plugin loading and registration."""
    print_separator("🔧 PLUGIN LOADING & REGISTRATION DEMO")

    # Initialize system components
    audio_event_bus = AudioEventBus()
    plugin_manager = PluginManager(audio_event_bus, plugin_dirs=[])
    manifest_loader = ManifestLoader()

    print("🧙‍♂️ Initializing Cognitive Geo-Thermal Lore Engine...")
    print(f"   Audio Event Bus: Ready")
    print(f"   Plugin Manager: Ready")
    print(f"   Manifest Loader: Ready")

    # Load and register sentiment lens plugin
    print("\n📊 Loading Sentiment Lens Plugin...")
    sentiment_manifest = manifest_loader.load_manifest("engine/plugins/examples/sentiment_lens/plugin.yaml")
    sentiment_metadata = create_metadata_from_manifest(manifest_loader, "engine/plugins/examples/sentiment_lens/plugin.yaml")
    sentiment_plugin = SentimentLensPlugin(sentiment_metadata)

    success = plugin_manager.register_plugin(sentiment_plugin)
    print(f"   Registration: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"   Capabilities: {[cap.value for cap in sentiment_plugin.get_capabilities()]}")

    # Load and register discourse tracker plugin
    print("\n💬 Loading Discourse Tracker Plugin...")
    discourse_manifest = manifest_loader.load_manifest("engine/plugins/examples/discourse_tracker/plugin.yaml")
    discourse_metadata = create_metadata_from_manifest(manifest_loader, "engine/plugins/examples/discourse_tracker/plugin.yaml")
    discourse_plugin = DiscourseTrackerPlugin(discourse_metadata)

    success = plugin_manager.register_plugin(discourse_plugin)
    print(f"   Registration: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"   Capabilities: {[cap.value for cap in discourse_plugin.get_capabilities()]}")

    # Show system stats
    stats = plugin_manager.get_plugin_stats()
    print(f"\n📈 System Status:")
    print(f"   Total Plugins: {stats['total_plugins']}")
    print(f"   Enabled Plugins: {stats['enabled_plugins']}")

    return audio_event_bus, plugin_manager, sentiment_plugin, discourse_plugin


def demo_cognitive_event_processing(audio_event_bus, sentiment_plugin, discourse_plugin):
    """Demonstrate cognitive event processing with plugins."""
    print_separator("🧠 COGNITIVE EVENT PROCESSING DEMO")

    # Sample cognitive events with different characteristics
    test_events = [
        {
            "type": AudioEventType.ANCHOR_ACTIVATED,
            "data": {
                "anchor_text": "This breakthrough discovery is absolutely amazing! The solution works brilliantly and I'm excited about the fantastic results."
            },
            "description": "Positive learning moment"
        },
        {
            "type": AudioEventType.CONFLICT_DETECTED,
            "data": {
                "conflict_description": "However, this approach has serious problems. The implementation is terrible and frustrating to work with."
            },
            "description": "Negative conflict with discourse markers"
        },
        {
            "type": AudioEventType.SUMMARY_GENERATED,
            "data": {
                "summary": "In conclusion, we need to balance innovation with stability. Therefore, the recommended approach combines proven methods with new techniques. Specifically, we should focus on incremental improvements."
            },
            "description": "Summary with rich discourse structure"
        },
        {
            "type": AudioEventType.ANCHOR_REINFORCED,
            "data": {
                "anchor_text": "The pattern recognition system is working effectively. Furthermore, the accuracy improvements are significant and noteworthy."
            },
            "description": "Neutral technical update with transitions"
        }
    ]

    print("🔄 Processing cognitive events through plugin system...\n")

    for i, event_info in enumerate(test_events, 1):
        print(f"Event {i}: {event_info['description']}")
        print(f"   Type: {event_info['type'].value}")

        # Create and publish event
        event_data = event_info["data"]
        audio_event_bus.publish(
            event_info["type"],
            event_data,
            intensity=0.7
        )

        # Brief pause for processing
        time.sleep(0.1)

        # Get immediate plugin results for demonstration
        test_event = AudioEvent(
            event_type=event_info["type"],
            timestamp=time.time(),
            data=event_data
        )

        # Process with sentiment plugin
        sentiment_result = sentiment_plugin.process_event(test_event)
        if sentiment_result and "sentiment_analysis" in sentiment_result:
            sentiment_score = sentiment_result["sentiment_analysis"]["score"]
            sentiment_icon = "😊" if sentiment_score > 0.2 else "😞" if sentiment_score < -0.2 else "😐"
            print(f"   Sentiment: {sentiment_score:.2f} {sentiment_icon}")

            if sentiment_result["sentiment_analysis"]["insights"]:
                for insight in sentiment_result["sentiment_analysis"]["insights"][:1]:  # Show first insight
                    print(f"   💡 {insight}")

        # Process with discourse plugin
        discourse_result = discourse_plugin.process_event(test_event)
        if discourse_result and "discourse_analysis" in discourse_result:
            markers = discourse_result["discourse_analysis"]["markers"]
            if markers:
                marker_categories = set(m["category"] for m in markers)
                print(f"   Discourse: {len(markers)} markers ({', '.join(marker_categories)})")

        print()

    print("✅ Event processing complete!")


def demo_plugin_insights(sentiment_plugin, discourse_plugin):
    """Demonstrate cognitive insights from plugins."""
    print_separator("🔍 COGNITIVE INSIGHTS DEMO")

    # Get insights from sentiment plugin
    print("📊 Sentiment Analysis Insights:")
    sentiment_insights = sentiment_plugin.get_cognitive_insights()

    if "sentiment_analysis" in sentiment_insights:
        analysis = sentiment_insights["sentiment_analysis"]

        if "sentiment_history_summary" in analysis:
            summary = analysis["sentiment_history_summary"]
            print(f"   Events Analyzed: {summary.get('total_events', 0)}")
            print(f"   Positive Events: {summary.get('positive_events', 0)}")
            print(f"   Negative Events: {summary.get('negative_events', 0)}")
            print(f"   Average Sentiment: {summary.get('average_sentiment', 0):.3f}")

        if "emotional_stability" in analysis:
            stability = analysis["emotional_stability"]
            stability_desc = "High" if stability > 0.7 else "Medium" if stability > 0.4 else "Low"
            print(f"   Emotional Stability: {stability:.3f} ({stability_desc})")

        if "dominant_emotional_themes" in analysis:
            themes = analysis["dominant_emotional_themes"]
            if themes:
                print(f"   Dominant Themes: {', '.join(themes)}")

    # Get insights from discourse plugin
    print("\n💬 Discourse Analysis Insights:")
    discourse_insights = discourse_plugin.get_cognitive_insights()

    if "discourse_analysis" in discourse_insights:
        analysis = discourse_insights["discourse_analysis"]

        if "discourse_history_summary" in analysis:
            summary = analysis["discourse_history_summary"]
            print(f"   Events Analyzed: {summary.get('total_events', 0)}")

            if "phase_distribution" in summary:
                phases = summary["phase_distribution"]
                if phases:
                    top_phase = max(phases.items(), key=lambda x: x[1])
                    print(f"   Dominant Phase: {top_phase[0]} ({top_phase[1]} events)")

        if "coherence_trends" in analysis:
            trends = analysis["coherence_trends"]
            if "trend" in trends and trends["trend"] != "insufficient_data":
                print(f"   Coherence Trend: {trends['trend']}")
                print(f"   Recent Average: {trends.get('recent_average', 0):.3f}")

        if "communication_quality" in analysis:
            quality = analysis["communication_quality"]
            print(f"   Discourse Richness: {quality.get('discourse_richness', 0)} unique markers")
            print(f"   Flow Quality: {quality.get('flow_assessment', {}).get('quality', 'unknown')}")


def demo_plugin_stats(plugin_manager, sentiment_plugin, discourse_plugin):
    """Demonstrate plugin statistics and performance metrics."""
    print_separator("📈 PLUGIN PERFORMANCE STATISTICS")

    # Individual plugin stats
    print("🔍 Individual Plugin Statistics:")

    sentiment_stats = sentiment_plugin.get_stats()
    print(f"\n📊 Sentiment Lens Plugin:")
    print(f"   Events Processed: {sentiment_stats['events_processed']}")
    print(f"   Average Execution Time: {sentiment_stats['average_execution_time_ms']:.2f}ms")
    print(f"   Error Rate: {sentiment_stats['error_rate']*100:.1f}%")
    print(f"   Status: {'🟢 Enabled' if sentiment_stats['enabled'] else '🔴 Disabled'}")

    discourse_stats = discourse_plugin.get_stats()
    print(f"\n💬 Discourse Tracker Plugin:")
    print(f"   Events Processed: {discourse_stats['events_processed']}")
    print(f"   Average Execution Time: {discourse_stats['average_execution_time_ms']:.2f}ms")
    print(f"   Error Rate: {discourse_stats['error_rate']*100:.1f}%")
    print(f"   Status: {'🟢 Enabled' if discourse_stats['enabled'] else '🔴 Disabled'}")

    # System-wide stats
    print(f"\n🏗️ Plugin Manager Statistics:")
    manager_stats = plugin_manager.get_plugin_stats()
    print(f"   Total Plugins: {manager_stats['total_plugins']}")
    print(f"   Enabled Plugins: {manager_stats['enabled_plugins']}")
    print(f"   Active Executions: {len(manager_stats.get('active_executions', {}))}")


def demo_manifest_validation():
    """Demonstrate plugin manifest validation."""
    print_separator("📋 PLUGIN MANIFEST VALIDATION DEMO")

    manifest_loader = ManifestLoader()

    # Test valid manifests
    print("✅ Testing Valid Manifests:")
    valid_manifests = [
        "engine/plugins/examples/sentiment_lens/plugin.yaml",
        "engine/plugins/examples/discourse_tracker/plugin.yaml"
    ]

    for manifest_path in valid_manifests:
        try:
            manifest_data = manifest_loader.load_manifest(manifest_path)
            print(f"   {manifest_path}: ✅ VALID")
            print(f"      Name: {manifest_data['name']} v{manifest_data['version']}")
            print(f"      Capabilities: {len(manifest_data['capabilities'])}")
        except Exception as e:
            print(f"   {manifest_path}: ❌ INVALID - {e}")

    # Test example manifest creation
    print(f"\n🔧 Example Manifest Generation:")
    example_manifest = manifest_loader.create_example_manifest("my_custom_plugin")
    print(f"   Generated manifest for: {example_manifest['name']}")
    print(f"   Default capabilities: {len(example_manifest['capabilities'])}")
    print(f"   Event subscriptions: {len(example_manifest['event_subscriptions'])}")


def main():
    """Main demo function."""
    print("🧙‍♂️" * 20)
    print("   COGNITIVE GEO-THERMAL LORE ENGINE v0.9")
    print("        Plugin Architecture Demo")
    print("🧙‍♂️" * 20)

    try:
        # Demo 1: Plugin Loading
        audio_event_bus, plugin_manager, sentiment_plugin, discourse_plugin = demo_plugin_loading()

        # Demo 2: Event Processing
        demo_cognitive_event_processing(audio_event_bus, sentiment_plugin, discourse_plugin)

        # Demo 3: Cognitive Insights
        demo_plugin_insights(sentiment_plugin, discourse_plugin)

        # Demo 4: Performance Stats
        demo_plugin_stats(plugin_manager, sentiment_plugin, discourse_plugin)

        # Demo 5: Manifest Validation
        demo_manifest_validation()

        print_separator("🎉 DEMO COMPLETE")
        print("🧙‍♂️ The plugin architecture is ready for your cognitive adventures!")
        print("   • Sentiment analysis provides emotional intelligence")
        print("   • Discourse tracking reveals communication patterns")
        print("   • Sandboxed execution ensures system stability")
        print("   • Manifest validation guarantees plugin quality")
        print("\n📚 Next steps:")
        print("   • Create your own plugins using the examples as templates")
        print("   • Extend the capability system for your specific needs")
        print("   • Integrate plugins into your cognitive workflows")
        print("\n🛡️ The Bootstrap Sentinel approves this implementation! 🛡️")

    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
