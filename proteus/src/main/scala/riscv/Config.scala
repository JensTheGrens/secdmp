package riscv

import spinal.core._
import riscv.plugins._

sealed trait BaseIsa {
  val xlen: Int
  val numRegs: Int
}

object BaseIsa {
  case object RV32I extends BaseIsa {
    override val xlen = 32
    override val numRegs = 32
  }
  case object RV32E extends BaseIsa {
    override val xlen = 32
    override val numRegs = 16
  }
  case object RV64I extends BaseIsa {
    override val xlen = 64
    override val numRegs = 32
  }
}

sealed trait PrefetcherType {

  /** Whether the prefetcher requires the PC to be passed to notifyLoadRequest and
    * notifyLoadResponse; when false, the PC signal will be set to null
    */
  val requiresPc: Boolean
}
object PrefetcherType {
  case object None extends PrefetcherType {
    override val requiresPc = false
  }
  case object SequentialInstructionPrefetcher extends PrefetcherType {
    override val requiresPc = false
  }
  case object BaseDmp extends PrefetcherType {
    override val requiresPc = false
  }
  case object BaseRecursiveDmp extends PrefetcherType {
    override val requiresPc = false
  }
  case object InfiniteRecursiveDmp extends PrefetcherType {
    override val requiresPc = false
  }
  case object AppleDmp extends PrefetcherType {
    override val requiresPc = false
  }
  case object IntelDmp extends PrefetcherType {
    override val requiresPc = true
  }
  case object Cdp extends PrefetcherType {
    override val requiresPc = false
  }
  case object Imp extends PrefetcherType {
    override val requiresPc = true
  }
}

case class PrefetcherConfig(prefetcherType: PrefetcherType) {
  def requiresPc: Boolean = prefetcherType.requiresPc

  def create(implicit config: Config): Option[Plugin[Pipeline] with PrefetchService] = {
    prefetcherType match {
      case PrefetcherType.None => None
      case PrefetcherType.SequentialInstructionPrefetcher =>
        Some(new memory.SequentialInstructionPrefetcher)
      case PrefetcherType.BaseDmp =>
        Some(
          new memory.PointerChasingDmp(
            pointerHeuristic = (address, value) => 0x80000000L <= value && value < 0xc0000000L,
            maxRecursionDepth = 0,
            nextLinePrefetches = 0,
            prefetchQueueSize = 4
          )
        )
      case PrefetcherType.BaseRecursiveDmp =>
        Some(
          new memory.PointerChasingDmp(
            pointerHeuristic = (address, value) => 0x80000000L <= value && value < 0xc0000000L,
            maxRecursionDepth = 1,
            nextLinePrefetches = 0,
            prefetchQueueSize = 4
          )
        )
      case PrefetcherType.InfiniteRecursiveDmp =>
        Some(
          new memory.PointerChasingDmp(
            pointerHeuristic = (address, value) => 0x80000000L <= value && value < 0xc0000000L,
            maxRecursionDepth = -1,
            nextLinePrefetches = 0,
            prefetchQueueSize = 4
          )
        )
      case PrefetcherType.AppleDmp =>
        Some(
          new memory.PointerChasingDmp(
            pointerHeuristic = (address, value) =>
              address.takeHigh(config.isa.xlen / 2) === value.takeHigh(config.isa.xlen / 2),
            maxRecursionDepth = 0,
            nextLinePrefetches = 1,
            prefetchQueueSize = 4
          )
        )
      case PrefetcherType.IntelDmp =>
        Some(
          new memory.ArrayOfPointersDmp(
            loadHistorySize = 8,
            prefetchQueueSize = 4,
            activationConfidence = 3,
            maxConfidence = 7,
            prefetchDistance = 16,
            alignmentBits = config.isa.xlen - 18,
            pcCompareBits = 10,
            strideDetectionLeniency = 1,
            pointerHeuristic = (_, _) => True
          )
        )
      case PrefetcherType.Cdp =>
        Some(
          new memory.PointerChasingDmp(
            pointerHeuristic = (address, value) => address.takeHigh(8) === value.takeHigh(8),
            maxRecursionDepth = 3,
            nextLinePrefetches = 3,
            prefetchQueueSize = 4
          )
        )
      case PrefetcherType.Imp =>
        Some(
          new memory.IndirectArrayPatternDmp(
            prefetchTableSize = 16,
            indirectPatternDetectorTableSize = 4,
            pcCompareBits = config.isa.xlen,
            shiftValues = Seq(2, 3, 4, -3),
            baseAddressArrayLength = 4,
            prefetchQueueSize = 4,
            strideActivationHitCount = 3,
            indirectActivationHitCount = 2,
            maxHitCount = 7,
            maxPrefetchDistance = 16,
            strideDetectionLeniency = 1,
            indirectVerificationLeniency = 4,
            pointerHeuristic = (_, _) => True
          )
        )
    }
  }
}

case class CacheConfig(
    sets: Int,
    ways: Int,
    prefetcher: PrefetcherConfig = PrefetcherConfig(PrefetcherType.None),
    maxPrefetches: Int = 1,
    delay: Int = 0
)

case class MemBusConfig(
    addressWidth: Int,
    idWidth: Int,
    dataWidth: Int,
    readWrite: Boolean = true,
    includePcWire: Boolean = false
) {
  def byte2WordAddress(ba: UInt): UInt = ba(dataWidth - 1 downto log2Up(dataWidth / 8))
  def word2ByteAddress(wa: UInt): UInt = wa << log2Up(dataWidth / 8)
}

sealed abstract class Config(
    val isa: BaseIsa,
    val memBusWidth: Int,
    val idWidth: Int,
    val extraDbusReadDelay: Int,
    val applyDelayToIBus: Boolean,
    val iCaches: Seq[CacheConfig],
    val dCaches: Seq[CacheConfig],
    val stlSpec: Boolean,
    val debug: Boolean
) {
  val internalIBusConfig = MemBusConfig(
    addressWidth = isa.xlen,
    idWidth = 2,
    dataWidth = memBusWidth,
    readWrite = false,
    includePcWire = iCaches.exists(_.prefetcher.requiresPc)
  )

  val externalIBusConfig = MemBusConfig(
    addressWidth = isa.xlen,
    idWidth = 2,
    dataWidth = memBusWidth,
    readWrite = false
  )

  val internalReadDBusConfig = MemBusConfig(
    addressWidth = isa.xlen,
    idWidth = idWidth,
    dataWidth = memBusWidth,
    readWrite = false,
    includePcWire = dCaches.exists(_.prefetcher.requiresPc)
  )

  val internalDBusConfig = MemBusConfig(
    addressWidth = isa.xlen,
    idWidth = idWidth,
    dataWidth = memBusWidth,
    includePcWire = dCaches.exists(_.prefetcher.requiresPc)
  )

  val externalDBusConfig = MemBusConfig(
    addressWidth = isa.xlen,
    idWidth = idWidth,
    dataWidth = memBusWidth
  )

  override def toString: String =
    s"""${getClass.getSimpleName}(
       |  isa=$isa,
       |  memBusWidth=$memBusWidth,
       |  idWidth=$idWidth,
       |  extraDbusReadDelay=$extraDbusReadDelay,
       |  applyDelayToIBus=$applyDelayToIBus,
       |  iCaches=$iCaches,
       |  dCaches=$dCaches,
       |  stlSpec=$stlSpec,
       |  debug=$debug
       |)""".stripMargin
}

class StaticPipelineConfig(
    isa: BaseIsa = BaseIsa.RV32I,
    memBusWidth: Int = 128,
    idWidth: Int = log2Up(4),
    extraDbusReadDelay: Int = 32,
    applyDelayToIBus: Boolean = false,
    iCaches: Seq[CacheConfig] = Seq(
      CacheConfig(
        sets = 2,
        ways = 2,
        prefetcher = PrefetcherConfig(PrefetcherType.SequentialInstructionPrefetcher)
      )
    ),
    dCaches: Seq[CacheConfig] = Seq(CacheConfig(sets = 8, ways = 2)),
    debug: Boolean = true
) extends Config(
      isa = isa,
      memBusWidth = memBusWidth,
      idWidth = idWidth,
      extraDbusReadDelay = extraDbusReadDelay,
      applyDelayToIBus = applyDelayToIBus,
      iCaches = iCaches,
      dCaches = dCaches,
      stlSpec = false,
      debug = debug
    )

class DynamicPipelineConfig(
    isa: BaseIsa = BaseIsa.RV32I,
    memBusWidth: Int = 128,
    extraDbusReadDelay: Int = 32,
    applyDelayToIBus: Boolean = false,
    iCaches: Seq[CacheConfig] = Seq(
      CacheConfig(
        sets = 2,
        ways = 2,
        prefetcher = PrefetcherConfig(PrefetcherType.SequentialInstructionPrefetcher)
      )
    ),
    dCaches: Seq[CacheConfig] = Seq(CacheConfig(sets = 8, ways = 2)),
    val robEntries: Int = 32,
    val parallelAlus: Int = 8,
    val parallelMulDivs: Int = 2,
    val parallelLoads: Int = 3,
    val addressBasedPsf: Boolean = true,
    val addressBasedSsb: Boolean = true,
    stlSpec: Boolean = true,
    debug: Boolean = true
) extends Config(
      isa = isa,
      memBusWidth = memBusWidth,
      idWidth = log2Up(parallelLoads + 1),
      extraDbusReadDelay = extraDbusReadDelay,
      applyDelayToIBus = applyDelayToIBus,
      iCaches = iCaches,
      dCaches = dCaches,
      stlSpec = stlSpec,
      debug = debug
    ) {
  override def toString: String =
    s"""${super.toString.dropRight(1)}
       |  robEntries=$robEntries,
       |  parallelAlus=$parallelAlus,
       |  parallelMulDivs=$parallelMulDivs,
       |  parallelLoads=$parallelLoads,
       |  addressBasedPsf=$addressBasedPsf,
       |  addressBasedSsb=$addressBasedSsb
       |)""".stripMargin
}

object Config {
  private def getPrefetcherType(prefetcher: String): PrefetcherType = {
    prefetcher match {
      case "None" => PrefetcherType.None
      case "SequentialInstructionPrefetcher" =>
        PrefetcherType.SequentialInstructionPrefetcher
      case "BaseDmp" => PrefetcherType.BaseDmp
      case "BaseRecursiveDmp" => PrefetcherType.BaseRecursiveDmp
      case "InfiniteRecursiveDmp" => PrefetcherType.InfiniteRecursiveDmp
      case "AppleDmp" => PrefetcherType.AppleDmp
      case "IntelDmp" => PrefetcherType.IntelDmp
      case "Cdp" => PrefetcherType.Cdp
      case "Imp" => PrefetcherType.Imp
      case other => throw new IllegalArgumentException(s"Unknown prefetcher: $other")
    }
  }

  private def getIsa(isa: String): BaseIsa = {
    isa match {
      case "RV32I" => BaseIsa.RV32I
      case "RV32E" => BaseIsa.RV32E
      case "RV64I" => BaseIsa.RV64I
      case other => throw new IllegalArgumentException(s"Unknown ISA: $other")
    }
  }

  def apply(jsonString: String): Config = {
    val jsonObject = ujson.read(jsonString)

    def parseBool(jsonObject: ujson.Value, key: String, default: Boolean): Boolean = {
      jsonObject.obj.get(key).map(_.bool).getOrElse(default)
    }

    def parseInt(jsonObject: ujson.Value, key: String, default: Int): Int = {
      jsonObject.obj.get(key).map(_.num.toInt).getOrElse(default)
    }

    def parseIsa(jsonObject: ujson.Value, key: String, default: BaseIsa): BaseIsa = {
      jsonObject.obj.get(key).map(_.str) match {
        case Some(isa) => getIsa(isa)
        case None => default
      }
    }

    def parsePrefetcher(
        jsonObject: ujson.Value,
        key: String,
        default: PrefetcherConfig
    ): PrefetcherConfig = {
      jsonObject.obj.get(key) match {
        case Some(prefetcher) =>
          PrefetcherConfig(prefetcher.obj.get("prefetcherType").map(_.str) match {
            case Some(prefetcherType) => getPrefetcherType(prefetcherType)
            case None => default.prefetcherType
          })
        case None => default
      }
    }

    def parseCaches(
        jsonObject: ujson.Value,
        key: String,
        default: CacheConfig
    ): Seq[CacheConfig] = {
      jsonObject.obj.get(key).map(_.arr) match {
        case Some(caches) => caches.map(cache => parseCache(cache, default))
        case None => Seq(default)
      }
    }

    def parseCache(cache: ujson.Value, default: CacheConfig): CacheConfig = {
      CacheConfig(
        sets = parseInt(cache, "sets", default.sets),
        ways = parseInt(cache, "ways", default.ways),
        prefetcher = parsePrefetcher(cache, "prefetcher", default.prefetcher),
        maxPrefetches = parseInt(cache, "maxPrefetches", default.maxPrefetches),
        delay = parseInt(cache, "delay", default.delay)
      )
    }

    jsonObject("pipeline").str match {
      case "Static" => {
        val default: StaticPipelineConfig = new StaticPipelineConfig()
        new StaticPipelineConfig(
          isa = parseIsa(jsonObject, "isa", default.isa),
          memBusWidth = parseInt(jsonObject, "memBusWidth", default.memBusWidth),
          idWidth = parseInt(jsonObject, "idWidth", default.idWidth),
          extraDbusReadDelay =
            parseInt(jsonObject, "extraDbusReadDelay", default.extraDbusReadDelay),
          applyDelayToIBus = parseBool(jsonObject, "applyDelayToIBus", default.applyDelayToIBus),
          iCaches = parseCaches(jsonObject, "iCaches", default.iCaches.head),
          dCaches = parseCaches(jsonObject, "dCaches", default.dCaches.head),
          debug = parseBool(jsonObject, "debug", default.debug)
        )
      }
      case "Dynamic" => {
        val default: DynamicPipelineConfig = new DynamicPipelineConfig()
        new DynamicPipelineConfig(
          isa = parseIsa(jsonObject, "isa", default.isa),
          memBusWidth = parseInt(jsonObject, "memBusWidth", default.memBusWidth),
          extraDbusReadDelay =
            parseInt(jsonObject, "extraDbusReadDelay", default.extraDbusReadDelay),
          applyDelayToIBus = parseBool(jsonObject, "applyDelayToIBus", default.applyDelayToIBus),
          iCaches = parseCaches(jsonObject, "iCaches", default.iCaches.head),
          dCaches = parseCaches(jsonObject, "dCaches", default.dCaches.head),
          robEntries = parseInt(jsonObject, "robEntries", default.robEntries),
          parallelAlus = parseInt(jsonObject, "parallelAlus", default.parallelAlus),
          parallelMulDivs = parseInt(jsonObject, "parallelMulDivs", default.parallelMulDivs),
          parallelLoads = parseInt(jsonObject, "parallelLoads", default.parallelLoads),
          addressBasedPsf = parseBool(jsonObject, "addressBasedPsf", default.addressBasedPsf),
          addressBasedSsb = parseBool(jsonObject, "addressBasedSsb", default.addressBasedSsb),
          stlSpec = parseBool(jsonObject, "stlSpec", default.stlSpec),
          debug = parseBool(jsonObject, "debug", default.debug)
        )
      }
      case other => throw new IllegalArgumentException(s"Unknown pipeline: $other")
    }
  }

  def apply(pipeline: String, isa: String): Config = {
    pipeline match {
      case "Static" => new StaticPipelineConfig(isa = getIsa(isa))
      case "Dynamic" => new DynamicPipelineConfig(isa = getIsa(isa))
      case other => throw new IllegalArgumentException(s"Unknown pipeline: $other")
    }
  }

  def secDmpConfig(prefetcher: String): DynamicPipelineConfig = {
    val prefetcherType = getPrefetcherType(prefetcher)
    new DynamicPipelineConfig(
      isa = BaseIsa.RV32I,
      extraDbusReadDelay = 64,
      applyDelayToIBus = false,
      dCaches = Seq(
        CacheConfig(
          sets = 16,
          ways = 4,
          prefetcher = PrefetcherConfig(prefetcherType),
          maxPrefetches = 1
        )
      )
    )
  }
}
