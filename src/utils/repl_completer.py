"""
Custom REPL completer with context-aware autocomplete.

Fixes multi-level command parameter position bug where Click's completer
shows completions from wrong parameter level.

Reads autocomplete directly from Typer command structure:
- Extracts autocompletion callbacks from Typer/Click command definitions
- Correctly tracks parameter position for multi-level commands
- Provides ONLY relevant suggestions for that specific parameter
- Calls the exact same autocomplete functions as shell completion

Single source of truth: Typer command definitions with autocompletion=... arguments!
"""

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from typing import Iterable, List, Optional
import click


class ContextAwareCompleter(Completer):
    """
    Parameter-aware completer that provides context-specific suggestions.
    
    Fixes Click's REPL completer bug where multi-level commands (e.g., "notes add")
    show completions from the wrong parameter position.
    
    Reads autocompletion callbacks directly from Typer/Click argument definitions,
    ensuring single source of truth while correctly tracking parameter positions.
    """
    
    def __init__(self, original_completer, click_ctx=None):
        """
        Initialize with the original click_repl completer.
        
        Args:
            original_completer: The original prompt_toolkit completer from click_repl
            click_ctx: Click context (to inspect command structure)
        """
        self.original_completer = original_completer
        self.click_ctx = click_ctx
    
    def get_completions(self, document: Document, complete_event) -> Iterable[Completion]:
        """
        Get completions with correct parameter position tracking.
        
        For commands/subcommands: delegates to original completer (with error handling)
        For parameters: extracts callback from Typer definition and calls it
        
        Args:
            document: Current document state
            complete_event: Completion event
            
        Yields:
            Completion objects for valid suggestions
        """
        text = document.text_before_cursor
        words = text.split()
        
        # If empty, show top-level commands
        if len(words) == 0:
            try:
                yield from self.original_completer.get_completions(document, complete_event)
            except Exception:
                pass
            return
        
        # If typing first word (command), show command completions
        if len(words) == 1 and not text.endswith(' '):
            try:
                yield from self.original_completer.get_completions(document, complete_event)
            except Exception:
                # Partial command that doesn't resolve yet
                pass
            return
        
        # Get the Click command structure
        if not self.click_ctx:
            return
        
        # Navigate to the actual command being executed
        ctx = self.click_ctx
        command = ctx.command
        
        # Track command depth and parameter offset
        cmd_depth = 0  # Number of command/subcommand words
        current_cmd = command
        
        # For multi-level commands like "notes add", navigate to the final command
        word_idx = 0
        while word_idx < len(words) and isinstance(current_cmd, click.MultiCommand):
            word = words[word_idx]
            subcommand = current_cmd.get_command(ctx, word)
            if subcommand:
                current_cmd = subcommand
                cmd_depth += 1
                word_idx += 1
            else:
                # Can't resolve this word as a subcommand
                # If we're typing the last word, show subcommand completions
                if word_idx == len(words) - 1 and not text.endswith(' '):
                    # Show available subcommands from current_cmd
                    if isinstance(current_cmd, click.MultiCommand):
                        for name in current_cmd.list_commands(ctx):
                            if name.lower().startswith(word.lower()):
                                yield Completion(name, start_position=-len(word))
                return
        
        # After navigation, check if we're still at a MultiCommand level
        # If yes and text ends with space, show subcommands
        if isinstance(current_cmd, click.MultiCommand) and text.endswith(' '):
            # Show subcommands (e.g., "notes " should show add, edit, list, etc.)
            for name in current_cmd.list_commands(ctx):
                yield Completion(name, start_position=0)
            return
        
        # Calculate parameter index (0-based)
        # If we have "notes add Alice ", we have:
        # - words = ['notes', 'add', 'Alice']
        # - cmd_depth = 2 (notes, add)
        # - text.endswith(' ') = True
        # - param_index = 3 - 2 = 1 (second parameter)
        if text.endswith(' '):
            param_index = len(words) - cmd_depth
        else:
            param_index = len(words) - cmd_depth - 1
        
        # If we're still typing command/subcommand or before first parameter
        if param_index < 0:
            # Show subcommand completions
            try:
                yield from self.original_completer.get_completions(document, complete_event)
            except Exception:
                pass
            return
        
        # Get the parameter at this position from the Click command
        params = [p for p in current_cmd.params if isinstance(p, click.Argument)]
        
        if param_index >= len(params):
            # Beyond defined parameters, no completion
            return
        
        param = params[param_index]
        
        # Extract autocompletion callback from parameter
        # Typer stores custom callbacks in _custom_shell_complete
        autocomplete_fn = None
        if hasattr(param, '_custom_shell_complete'):
            autocomplete_fn = param._custom_shell_complete
        elif hasattr(param, 'autocompletion') and param.autocompletion:
            autocomplete_fn = param.autocompletion
        
        if not autocomplete_fn:
            # No autocomplete defined for this parameter - show nothing
            return
        
        # Get current word being typed
        if text.endswith(' '):
            current_word = ''
        else:
            current_word = words[-1] if words else ''
        
        # Build context with previously entered parameters
        ctx_params = {}
        for i, prev_param in enumerate(params[:param_index]):
            param_word_idx = cmd_depth + i
            if param_word_idx < len(words):
                ctx_params[prev_param.name] = words[param_word_idx]
        
        # Create a minimal Click context for the autocomplete callback
        fake_ctx = click.Context(current_cmd)
        fake_ctx.params = ctx_params
        
        # Call the autocomplete function
        # Signature: (ctx, args, incomplete) -> List[CompletionItem] or List[str]
        try:
            suggestions = autocomplete_fn(fake_ctx, [], current_word)
            if suggestions:
                for suggestion in suggestions:
                    # Handle both CompletionItem objects and strings
                    if hasattr(suggestion, 'value'):
                        # It's a CompletionItem
                        text = suggestion.value
                    elif isinstance(suggestion, str):
                        text = suggestion
                    else:
                        continue
                    
                    # Filter by current word
                    if text.lower().startswith(current_word.lower()):
                        yield Completion(text, start_position=-len(current_word))
        except Exception as e:
            # If autocomplete fails, don't show anything
            pass


def create_context_aware_completer(click_completer, click_ctx=None):
    """
    Create a context-aware completer wrapper.
    
    Args:
        click_completer: The original Click completer
        click_ctx: Click context (to inspect command structure)
        
    Returns:
        ContextAwareCompleter instance
    """
    return ContextAwareCompleter(click_completer, click_ctx)

