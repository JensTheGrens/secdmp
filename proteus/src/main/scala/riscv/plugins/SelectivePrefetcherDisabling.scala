package riscv.plugins

import riscv._
import spinal.core._
import spinal.lib._

class SelectivePrefetcherDisabling
    extends Plugin[Pipeline]
    with SelectivePrefetcherDisablingService {
  override def setup(): Unit = {
    assert(
      pipeline.hasService[SecurityService],
      "Security service required for selective prefetcher disabling"
    )
  }
}
